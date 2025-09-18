from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.views.decorators.http import require_http_methods
from asgiref.sync import sync_to_async
import json
import uuid
import os
import logging
import asyncio
from typing import Dict, List
from .models import (
    ChatSession, ChatMessage, Symptom, Disease, PatientSymptom, 
    AIRecommendation, MedicineInfo, MedicalImage, ImageAnalysis,
    AIDiagnosis, HealthMetrics, EmergencyAlert
)
from .services import MedicalAIService, DoctorRecommendationService
from .advanced_ai_service import advanced_ai_service
from django.db.models import Q

# Initialize AI services
ai_service = MedicalAIService()
recommendation_service = DoctorRecommendationService()
logger = logging.getLogger(__name__)

# Chatbot interface
@login_required
def chatbot_interface(request):
    """Display the advanced AI chatbot interface."""
    # Get or create active chat session
    active_session, created = ChatSession.objects.get_or_create(
        user=request.user,
        is_active=True,
        defaults={'session_id': str(uuid.uuid4())}
    )
    
    # Get recent messages
    recent_messages = ChatMessage.objects.filter(session=active_session).order_by('-timestamp')[:10]
    
    # Get user's health metrics if available
    try:
        latest_metrics = HealthMetrics.objects.filter(user=request.user).order_by('-recorded_at').first()
    except:
        latest_metrics = None
    
    context = {
        'current_time': timezone.now().strftime('%H:%M'),
        'session_id': active_session.session_id,
        'recent_messages': recent_messages,
        'latest_metrics': latest_metrics,
    }
    return render(request, 'chatbot/chatbot_interface.html', context)

@login_required
def start_chat_session(request):
    """Start a new chat session."""
    if request.method == 'POST':
        # End any existing active session
        ChatSession.objects.filter(user=request.user, is_active=True).update(is_active=False)
        
        # Create new session
        session = ChatSession.objects.create(
            user=request.user,
            session_id=str(uuid.uuid4()),
            is_active=True
        )
        
        # Add welcome message
        welcome_message = ChatMessage.objects.create(
            session=session,
            message_type='BOT',
            content="Hello! I'm your AI Health Assistant. I can help you with:\n\n" +
                   "🔍 Symptom analysis and diagnosis\n" +
                   "📸 Medical image analysis (X-rays, MRIs, blood reports)\n" +
                   "💊 Medicine information and interactions\n" +
                   "🏥 Doctor and hospital recommendations\n" +
                   "📊 Health metrics monitoring\n" +
                   "🚨 Emergency alerts and guidance\n\n" +
                   "How can I help you today?"
        )
        
        return JsonResponse({
            'success': True,
            'session_id': session.session_id,
            'welcome_message': welcome_message.content
        })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def end_chat_session(request, session_id):
    """End an existing chat session."""
    try:
        session = ChatSession.objects.get(session_id=session_id, user=request.user)
        session.end_session()
        return JsonResponse({'success': True})
    except ChatSession.DoesNotExist:
        return JsonResponse({'error': 'Session not found'}, status=404)

@login_required
def send_message(request, session_id):
    """Process a message sent to the AI chatbot using advanced AI service."""
    if request.method == 'POST':
        try:
            session = ChatSession.objects.get(session_id=session_id, user=request.user)
        except ChatSession.DoesNotExist:
            return JsonResponse({'error': 'Session not found'}, status=404)
        
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        ai_provider = data.get('ai_provider', 'auto')  # Allow user to select AI provider
        
        if not user_message:
            return JsonResponse({'error': 'Message cannot be empty'}, status=400)
        
        # Save user message
        user_msg = ChatMessage.objects.create(
            session=session,
            message_type='USER',
            content=user_message
        )
        
        # Prepare context for AI
        context = prepare_user_context(session, user_message)
        
        # Process message with advanced AI service (sync wrapper)
        try:
            ai_response = asyncio.run(advanced_ai_service.get_ai_response(
                user_message, 
                context=context, 
                provider=ai_provider
            ))
        except Exception as e:
            logger.error(f"Error in advanced AI service: {str(e)}")
            # Provide a fallback response instead of error
            ai_response = {
                'success': True, 
                'response': f"I understand you said: '{user_message}'. I'm here to help with your health questions. Could you please provide more details about your symptoms or health concerns?"
            }
        
        # Ensure we always have a valid response
        if not ai_response or not ai_response.get('success'):
            ai_response = {
                'success': True, 
                'response': f"I understand you said: '{user_message}'. I'm here to help with your health questions. Could you please provide more details about your symptoms or health concerns?"
            }
        
        if ai_response['success']:
            # Save AI response
            bot_msg = ChatMessage.objects.create(
                session=session,
                message_type='BOT',
                content=ai_response['response']
            )
            
            # Save analysis if available
            if ai_response.get('analysis'):
                save_ai_analysis(session, ai_response['analysis'])
            
            return JsonResponse({
                'success': True,
                'user_message': user_message,
                'ai_response': ai_response['response'],
                'timestamp': timezone.now().strftime('%H:%M'),
                'analysis': ai_response.get('analysis'),
                'recommendations': ai_response.get('recommendations'),
                'emergency_alert': ai_response.get('emergency_alert', False),
                'ai_provider': ai_response.get('provider', 'unknown'),
                'confidence': ai_response.get('confidence', 0.8)
            })
        else:
            # Fallback to basic AI service
            fallback_response = process_user_message(user_message, session)
            
            bot_msg = ChatMessage.objects.create(
                session=session,
                message_type='BOT',
                content=fallback_response['response']
            )
            
            return JsonResponse({
                'success': True,
                'user_message': user_message,
                'ai_response': fallback_response['response'],
                'timestamp': timezone.now().strftime('%H:%M'),
                'analysis': fallback_response.get('analysis'),
                'recommendations': fallback_response.get('recommendations'),
                'emergency_alert': fallback_response.get('emergency_alert', False),
                'ai_provider': 'fallback',
                'confidence': 0.6
            })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

def prepare_user_context(session: ChatSession, user_message: str) -> Dict:
    """Prepare user context for AI processing."""
    context = {}
    
    # Get recent messages for context
    recent_messages = ChatMessage.objects.filter(session=session).order_by('-timestamp')[:5]
    context['conversation_history'] = [
        {'type': msg.message_type, 'content': msg.content, 'timestamp': msg.timestamp}
        for msg in recent_messages
    ]
    
    # Get user's health metrics
    try:
        latest_metrics = HealthMetrics.objects.filter(user=session.user).order_by('-recorded_at').first()
        if latest_metrics:
            context['vital_signs'] = {
                'blood_pressure': f"{latest_metrics.blood_pressure_systolic}/{latest_metrics.blood_pressure_diastolic}",
                'heart_rate': latest_metrics.heart_rate,
                'temperature': latest_metrics.temperature,
                'weight': latest_metrics.weight
            }
    except:
        pass
    
    # Get user's medical history from profile
    try:
        user_profile = session.user.profile
        if hasattr(user_profile, 'medical_history') and user_profile.medical_history:
            context['medical_history'] = user_profile.medical_history
        if hasattr(user_profile, 'current_medications') and user_profile.current_medications:
            context['current_medications'] = user_profile.current_medications.split(',')
    except:
        pass
    
    # Extract symptoms from message
    symptoms = extract_symptoms_from_message(user_message)
    if symptoms:
        context['symptoms'] = symptoms
    
    return context

def extract_symptoms_from_message(message: str) -> List[str]:
    """Extract potential symptoms from user message."""
    symptom_keywords = [
        'fever', 'headache', 'pain', 'ache', 'nausea', 'dizziness', 'fatigue',
        'cough', 'sore throat', 'runny nose', 'chest pain', 'shortness of breath',
        'abdominal pain', 'stomach ache', 'back pain', 'joint pain', 'muscle pain',
        'rash', 'swelling', 'bleeding', 'numbness', 'tingling', 'weakness'
    ]
    
    message_lower = message.lower()
    found_symptoms = []
    
    for symptom in symptom_keywords:
        if symptom in message_lower:
            found_symptoms.append(symptom)
    
    return found_symptoms

def save_ai_analysis(session: ChatSession, analysis: Dict):
    """Save AI analysis to database."""
    try:
        if 'possible_diseases' in analysis:
            # Create AI diagnosis record
            ai_diagnosis = AIDiagnosis.objects.create(
                user=session.user,
                diagnosis_type='SYMPTOM_ANALYSIS',
                predicted_disease=analysis['possible_diseases'][0] if analysis['possible_diseases'] else 'Unknown',
                confidence_score=analysis.get('confidence_score', 0.0),
                recommendations=analysis.get('recommendations', []),
                raw_analysis=analysis
            )
            
            return ai_diagnosis
    except Exception as e:
        logger.error(f"Error saving AI analysis: {str(e)}")
        return None

def process_user_message(message: str, session: ChatSession) -> dict:
    """Process user message and generate AI response."""
    message_lower = message.lower()
    
    # Check for emergency keywords
    emergency_keywords = ['emergency', 'urgent', 'critical', 'severe', 'unconscious', 'bleeding']
    if any(keyword in message_lower for keyword in emergency_keywords):
        return {
            'response': "🚨 EMERGENCY ALERT! This sounds serious. Please:\n\n" +
                       "1. Call emergency services immediately (911/112)\n" +
                       "2. Go to the nearest emergency room\n" +
                       "3. Do not delay seeking medical help\n\n" +
                       "Can you tell me more about what's happening?",
            'emergency_alert': True
        }
    
    # Check for symptom reporting
    if any(word in message_lower for word in ['symptom', 'symptoms', 'feeling', 'experiencing', 'have']):
        return process_symptom_analysis(message, session)
    
    # Check for image upload request
    if any(word in message_lower for word in ['image', 'photo', 'picture', 'scan', 'xray', 'mri', 'report']):
        return {
            'response': "📸 I can analyze medical images for you! Please upload your image and I'll provide an AI-powered analysis.\n\n" +
                       "Supported formats: X-rays, MRIs, CT scans, ultrasounds, blood reports, ECG reports, and pathology reports.\n\n" +
                       "Click the image upload button below to get started."
        }
    
    # Check for medicine queries
    if any(word in message_lower for word in ['medicine', 'medication', 'drug', 'pill', 'tablet']):
        return process_medicine_query(message)
    
    # Check for health metrics
    if any(word in message_lower for word in ['blood pressure', 'heart rate', 'temperature', 'weight', 'height']):
        return {
            'response': "📊 I can help you monitor your health metrics! Please share your vital signs and I'll analyze them for any abnormalities.\n\n" +
                       "You can input:\n" +
                       "• Blood pressure (systolic/diastolic)\n" +
                       "• Heart rate\n" +
                       "• Temperature\n" +
                       "• Blood sugar\n" +
                       "• Weight and height\n\n" +
                       "What would you like to check?"
        }
    
    # Check for doctor/hospital recommendations
    if any(word in message_lower for word in ['doctor', 'hospital', 'specialist', 'appointment']):
        return {
            'response': "🏥 I can recommend doctors and hospitals based on your needs! To provide the best recommendations, I'll need to know:\n\n" +
                       "1. What symptoms or condition you're experiencing\n" +
                       "2. Your preferred location (city/area)\n" +
                       "3. Any specific requirements (specialization, budget, etc.)\n\n" +
                       "Please share your symptoms first, and I'll find the right healthcare providers for you."
        }
    
    # Default response
    return {
        'response': "I'm here to help with your health concerns! I can:\n\n" +
                   "🔍 Analyze symptoms and provide preliminary diagnosis\n" +
                   "📸 Analyze medical images (X-rays, MRIs, reports)\n" +
                   "💊 Provide medicine information\n" +
                   "🏥 Recommend doctors and hospitals\n" +
                   "📊 Monitor health metrics\n" +
                   "🚨 Provide emergency guidance\n\n" +
                   "What would you like help with today?"
    }

def process_symptom_analysis(message: str, session: ChatSession) -> dict:
    """Process symptom analysis with AI."""
    # Extract symptoms from message (simplified for demo)
    common_symptoms = [
        'fever', 'headache', 'cough', 'chest pain', 'abdominal pain', 'nausea',
        'vomiting', 'diarrhea', 'fatigue', 'dizziness', 'shortness of breath',
        'joint pain', 'back pain', 'neck pain', 'sore throat', 'runny nose'
    ]
    
    detected_symptoms = []
    for symptom in common_symptoms:
        if symptom in message.lower():
            detected_symptoms.append(symptom)
    
    if not detected_symptoms:
        return {
            'response': "I couldn't identify specific symptoms in your message. Could you please describe what you're experiencing in more detail?\n\n" +
                       "For example: 'I have a fever and headache' or 'I'm experiencing chest pain and shortness of breath'"
        }
    
    # Analyze symptoms with AI
    analysis = ai_service.analyze_symptoms(detected_symptoms)
    
    # Generate response
    response = f"🔍 **Symptom Analysis Results**\n\n"
    response += f"**Detected Symptoms:** {', '.join(detected_symptoms).title()}\n\n"
    
    if analysis.get('possible_diseases'):
        response += "**Possible Conditions:**\n"
        for disease, data in analysis['possible_diseases'][:3]:
            confidence = int(data['final_confidence'] * 100)
            response += f"• {disease} (Confidence: {confidence}%)\n"
        response += "\n"
    
    response += f"**Urgency Level:** {analysis['urgency_level'].replace('_', ' ').title()}\n"
    response += f"**AI Confidence:** {int(analysis['confidence_score'] * 100)}%\n\n"
    
    if analysis.get('recommendations'):
        response += "**Recommendations:**\n"
        for rec in analysis['recommendations'][:3]:
            response += f"• {rec}\n"
        response += "\n"
    
    # Check for emergency
    if analysis.get('emergency_alert'):
        response += "🚨 **EMERGENCY ALERT:** " + analysis['emergency_alert']['message'] + "\n\n"
        response += "**Immediate Actions:**\n"
        for action in analysis['emergency_alert']['actions']:
            response += f"• {action}\n"
    
    # Get doctor recommendations
    recommendations = recommendation_service.get_recommendations(analysis)
    
    return {
        'response': response,
        'analysis': analysis,
        'recommendations': recommendations,
        'emergency_alert': analysis.get('emergency_alert')
    }

def process_medicine_query(message: str) -> dict:
    """Process medicine-related queries."""
    # This would integrate with a medicine database in production
    return {
        'response': "💊 I can provide information about medicines, including:\n\n" +
                   "• Dosage and usage instructions\n" +
                   "• Side effects and contraindications\n" +
                   "• Drug interactions\n" +
                   "• Generic alternatives\n\n" +
                   "Please specify which medicine you'd like information about, or describe your symptoms so I can suggest appropriate medications.\n\n" +
                   "**Note:** Always consult with a healthcare professional before taking any medication."
    }

@login_required
@csrf_exempt
def upload_medical_image(request):
    """Handle medical image uploads for AI analysis."""
    if request.method == 'POST':
        try:
            session_id = request.POST.get('session_id')
            session = ChatSession.objects.get(session_id=session_id, user=request.user)
        except ChatSession.DoesNotExist:
            return JsonResponse({'error': 'Session not found'}, status=404)
        
        if 'image' not in request.FILES:
            return JsonResponse({'error': 'No image uploaded'}, status=400)
        
        image_file = request.FILES['image']
        image_type = request.POST.get('image_type', 'OTHER')
        description = request.POST.get('description', '')
        
        # Save image
        image_path = f'medical_images/{session_id}/{image_file.name}'
        saved_path = default_storage.save(image_path, ContentFile(image_file.read()))
        
        # Create medical image record
        medical_image = MedicalImage.objects.create(
            chat_session=session,
            image=saved_path,
            image_type=image_type,
            description=description
        )
        
        # Analyze image with AI
        analysis_result = ai_service.analyze_medical_image(image_type, description)
        
        # Save analysis
        image_analysis = ImageAnalysis.objects.create(
            medical_image=medical_image,
            analysis_text=analysis_result['analysis_text'],
            detected_conditions=analysis_result['detected_conditions'],
            confidence_score=analysis_result['confidence_score'],
            recommendations='\n'.join(analysis_result['recommendations'])
        )
        
        # Generate response
        response = f"📸 **Medical Image Analysis Complete**\n\n"
        response += f"**Image Type:** {medical_image.get_image_type_display()}\n"
        response += f"**Analysis:** {analysis_result['analysis_text']}\n\n"
        
        if analysis_result.get('critical_findings'):
            response += "🚨 **Critical Findings Detected:**\n"
            for finding in analysis_result['critical_findings']:
                response += f"• {finding['message']}\n"
            response += "\n"
        
        if analysis_result.get('recommendations'):
            response += "**Recommendations:**\n"
            for rec in analysis_result['recommendations']:
                response += f"• {rec}\n"
        
        # Save bot response
        ChatMessage.objects.create(
            session=session,
            message_type='BOT',
            content=response
        )
        
        return JsonResponse({
            'success': True,
            'analysis': analysis_result,
            'response': response
        })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
@csrf_exempt
def record_health_metrics(request):
    """Record and analyze health metrics."""
    if request.method == 'POST':
        try:
            session_id = request.POST.get('session_id')
            session = ChatSession.objects.get(session_id=session_id, user=request.user)
        except ChatSession.DoesNotExist:
            return JsonResponse({'error': 'Session not found'}, status=404)
        
        # Extract metrics from form
        metrics_data = {}
        metric_fields = ['blood_pressure_systolic', 'blood_pressure_diastolic', 'heart_rate', 
                        'temperature', 'blood_sugar', 'weight', 'height']
        
        for field in metric_fields:
            value = request.POST.get(field)
            if value and value.strip():
                try:
                    if field in ['weight', 'height', 'temperature']:
                        metrics_data[field] = float(value)
                    else:
                        metrics_data[field] = int(value)
                except ValueError:
                    continue
        
        if not metrics_data:
            return JsonResponse({'error': 'No valid metrics provided'}, status=400)
        
        # Save health metrics
        health_metrics = HealthMetrics.objects.create(
            chat_session=session,
            **metrics_data
        )
        
        # Analyze metrics with AI
        analysis = ai_service.analyze_health_metrics(metrics_data)
        
        # Generate response
        response = f"📊 **Health Metrics Analysis**\n\n"
        response += f"**Overall Status:** {analysis['overall_status']}\n\n"
        
        if analysis.get('alerts'):
            response += "**Alerts:**\n"
            for alert in analysis['alerts']:
                severity_icon = "🚨" if alert['severity'] == 'CRITICAL' else "⚠️"
                response += f"{severity_icon} {alert['message']}\n"
            response += "\n"
        
        if analysis.get('recommendations'):
            response += "**Recommendations:**\n"
            for rec in analysis['recommendations']:
                response += f"• {rec}\n"
        
        # Save bot response
        ChatMessage.objects.create(
            session=session,
            message_type='BOT',
            content=response
        )
        
        return JsonResponse({
            'success': True,
            'analysis': analysis,
            'response': response
        })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def get_doctor_recommendations(request):
    """Get AI-powered doctor and hospital recommendations."""
    if request.method == 'POST':
        try:
            session_id = request.POST.get('session_id')
            session = ChatSession.objects.get(session_id=session_id, user=request.user)
        except ChatSession.DoesNotExist:
            return JsonResponse({'error': 'Session not found'}, status=404)
        
        symptoms = request.POST.get('symptoms', '').split(',')
        location = request.POST.get('location', '')
        
        # Analyze symptoms
        analysis = ai_service.analyze_symptoms(symptoms)
        
        # Get recommendations
        recommendations = recommendation_service.get_recommendations(analysis, location)
        
        # Generate response
        response = "🏥 **AI-Powered Healthcare Recommendations**\n\n"
        
        if recommendations.get('doctors'):
            response += "**Recommended Doctors:**\n"
            for doctor in recommendations['doctors'][:5]:
                response += f"• Dr. {doctor['name']} - {doctor['specialization']}\n"
                response += f"  Experience: {doctor['experience_years']} years\n"
                response += f"  Hospital: {doctor['hospital_name']}\n"
                response += f"  Fee: ₹{doctor['consultation_fee']}\n\n"
        
        if recommendations.get('hospitals'):
            response += "**Recommended Hospitals:**\n"
            for hospital in recommendations['hospitals'][:3]:
                response += f"• {hospital['name']} - {hospital['type']}\n"
                response += f"  Address: {hospital['address']}\n"
                response += f"  Specialization: {hospital['specialization']}\n\n"
        
        # Save bot response
        ChatMessage.objects.create(
            session=session,
            message_type='BOT',
            content=response
        )
        
        return JsonResponse({
            'success': True,
            'recommendations': recommendations,
            'response': response
        })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

# Symptom and disease related
@login_required
def symptoms_list(request):
    """Display list of symptoms."""
    symptoms = Symptom.objects.all().order_by('name')
    context = {
        'symptoms': symptoms,
    }
    return render(request, 'chatbot/symptoms_list.html', context)

@login_required
def symptom_detail(request, symptom_id):
    """Display details of a specific symptom."""
    symptom = get_object_or_404(Symptom, id=symptom_id)
    context = {
        'symptom': symptom,
    }
    return render(request, 'chatbot/symptom_detail.html', context)

@login_required
def diseases_list(request):
    """Display list of diseases."""
    diseases = Disease.objects.all().order_by('name')
    context = {
        'diseases': diseases,
    }
    return render(request, 'chatbot/diseases_list.html', context)

@login_required
def disease_detail(request, disease_id):
    """Display details of a specific disease."""
    disease = get_object_or_404(Disease, id=disease_id)
    context = {
        'disease': disease,
    }
    return render(request, 'chatbot/disease_detail.html', context)

# Medicine information
@login_required
def medicines_list(request):
    """Display list of medicines."""
    medicines = MedicineInfo.objects.all().order_by('name')
    context = {
        'medicines': medicines,
    }
    return render(request, 'chatbot/medicines_list.html', context)

@login_required
def medicine_detail(request, medicine_id):
    """Display details of a specific medicine."""
    medicine = get_object_or_404(MedicineInfo, id=medicine_id)
    context = {
        'medicine': medicine,
    }
    return render(request, 'chatbot/medicine_detail.html', context)

@login_required
def search_medicines(request):
    """Search for medicines."""
    query = request.GET.get('query', '')
    if query:
        medicines = MedicineInfo.objects.filter(
            Q(name__icontains=query) | Q(generic_name__icontains=query)
        )
    else:
        medicines = MedicineInfo.objects.all()
    
    context = {
        'medicines': medicines,
        'query': query,
    }
    return render(request, 'chatbot/medicines_list.html', context)

# AI recommendations
@login_required
def recommendations(request, session_id):
    """Display AI recommendations for a chat session."""
    try:
        session = ChatSession.objects.get(session_id=session_id, user=request.user)
        recommendations = AIRecommendation.objects.filter(chat_session=session).order_by('-created_at')
    except ChatSession.DoesNotExist:
        recommendations = []
    
    context = {
        'recommendations': recommendations,
        'session_id': session_id,
    }
    return render(request, 'chatbot/recommendations.html', context)

# History of chat sessions
@login_required
def chat_history(request):
    """Display history of user's chat sessions."""
    sessions = ChatSession.objects.filter(user=request.user).order_by('-started_at')
    context = {
        'sessions': sessions,
    }
    return render(request, 'chatbot/chat_history.html', context)

@login_required
def chat_session_detail(request, session_id):
    """Display details of a specific chat session."""
    try:
        session = ChatSession.objects.get(session_id=session_id, user=request.user)
        messages = ChatMessage.objects.filter(session=session).order_by('timestamp')
        
        # Get related data
        medical_images = MedicalImage.objects.filter(chat_session=session)
        health_metrics = HealthMetrics.objects.filter(chat_session=session)
        ai_diagnoses = AIDiagnosis.objects.filter(chat_session=session)
        emergency_alerts = EmergencyAlert.objects.filter(chat_session=session)
        
    except ChatSession.DoesNotExist:
        session = None
        messages = []
        medical_images = []
        health_metrics = []
        ai_diagnoses = []
        emergency_alerts = []
    
    context = {
        'session': session,
        'messages': messages,
        'medical_images': medical_images,
        'health_metrics': health_metrics,
        'ai_diagnoses': ai_diagnoses,
        'emergency_alerts': emergency_alerts,
    }
    return render(request, 'chatbot/chat_session_detail.html', context)
