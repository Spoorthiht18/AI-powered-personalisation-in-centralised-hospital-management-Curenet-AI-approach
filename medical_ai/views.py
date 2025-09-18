"""
Medical AI Views for Live Disease Diagnosis
"""

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import json
import logging
from .live_diagnosis import live_diagnosis
from .models import AIDiagnosis, MedicalImage, ImageAnalysis, MedicalReport, DiagnosisSession

logger = logging.getLogger(__name__)

# Basic views that were missing
@login_required
def upload_report(request):
    """Upload medical report"""
    if request.method == 'POST':
        # Handle file upload
        report_file = request.FILES.get('report_file')
        report_type = request.POST.get('report_type', 'OTHER')
        
        if report_file:
            report = MedicalReport.objects.create(
                patient=request.user,
                report_type=report_type,
                report_file=report_file
            )
            return JsonResponse({'success': True, 'report_id': report.id})
    
    return render(request, 'medical_ai/upload_report.html')

@login_required
def symptom_checker(request):
    """Symptom checker interface"""
    return render(request, 'medical_ai/symptom_checker.html')

@login_required
def get_symptom_questions(request):
    """Get symptom questions for diagnosis"""
    # Return basic symptom questions
    questions = [
        {'id': 1, 'question': 'Do you have a fever?', 'symptom': 'fever'},
        {'id': 2, 'question': 'Are you experiencing chest pain?', 'symptom': 'chest_pain'},
        {'id': 3, 'question': 'Do you have difficulty breathing?', 'symptom': 'shortness_of_breath'},
        {'id': 4, 'question': 'Are you experiencing headaches?', 'symptom': 'headache'},
        {'id': 5, 'question': 'Do you have a cough?', 'symptom': 'cough'},
    ]
    return JsonResponse({'questions': questions})

@login_required
def view_report_analysis(request, report_id):
    """View analysis of uploaded report"""
    try:
        report = MedicalReport.objects.get(id=report_id, patient=request.user)
        return render(request, 'medical_ai/report_analysis.html', {'report': report})
    except MedicalReport.DoesNotExist:
        return JsonResponse({'error': 'Report not found'}, status=404)

@login_required
def analyze_image(request):
    """Analyze uploaded medical image"""
    if request.method == 'POST':
        image_file = request.FILES.get('image')
        if image_file:
            # Basic analysis - you can enhance this
            return JsonResponse({
                'success': True,
                'analysis': 'Image analysis completed',
                'recommendations': ['Consult a healthcare professional']
            })
    
    return JsonResponse({'error': 'No image provided'}, status=400)

@login_required
def live_diagnosis_camera(request):
    """Live camera diagnosis interface"""
    return render(request, 'medical_ai/live_diagnosis.html')

@csrf_exempt
@require_http_methods(["POST"])
def capture_and_diagnose(request):
    """Capture image from camera and diagnose"""
    try:
        data = json.loads(request.body)
        image_data = data.get('image')
        
        if not image_data:
            return JsonResponse({'error': 'No image data provided'}, status=400)
        
        # Process the image
        result = live_diagnosis.process_live_capture(image_data)
        
        if 'error' in result:
            return JsonResponse(result, status=500)
        
        # Save diagnosis to database
        if result['success']:
            diagnosis = AIDiagnosis.objects.create(
                user=request.user,
                diagnosis_type='LIVE_CAMERA',
                predicted_disease=result['predicted_disease'],
                confidence_score=result['confidence'],
                recommendations=json.dumps(result['recommendations']),
                raw_analysis=json.dumps(result)
            )
            
            # Add diagnosis ID to response
            result['diagnosis_id'] = diagnosis.id
        
        return JsonResponse(result)
        
    except Exception as e:
        logger.error(f"Error in capture_and_diagnose: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def upload_and_diagnose(request):
    """Upload image file and diagnose"""
    try:
        if 'image' not in request.FILES:
            return JsonResponse({'error': 'No image file provided'}, status=400)
        
        image_file = request.FILES['image']
        
        # Save uploaded image
        medical_image = MedicalImage.objects.create(
            user=request.user,
            image=image_file,
            image_type='UPLOADED'
        )
        
        # Read image for processing
        import numpy as np
        from PIL import Image
        
        image = Image.open(image_file)
        image = np.array(image)
        
        # Get diagnosis
        result = live_diagnosis.predict_disease(image)
        
        if 'error' not in result and result['success']:
            # Save analysis
            analysis = ImageAnalysis.objects.create(
                medical_image=medical_image,
                predicted_disease=result['predicted_disease'],
                confidence_score=result['confidence'],
                analysis_data=json.dumps(result)
            )
            
            # Create diagnosis record
            diagnosis = AIDiagnosis.objects.create(
                user=request.user,
                diagnosis_type='UPLOADED_IMAGE',
                predicted_disease=result['predicted_disease'],
                confidence_score=result['confidence'],
                recommendations=json.dumps(result['recommendations']),
                raw_analysis=json.dumps(result)
            )
            
            result['diagnosis_id'] = diagnosis.id
            result['image_id'] = medical_image.id
        
        return JsonResponse(result)
        
    except Exception as e:
        logger.error(f"Error in upload_and_diagnose: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def diagnosis_history(request):
    """View diagnosis history"""
    diagnoses = AIDiagnosis.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'medical_ai/diagnosis_history.html', {'diagnoses': diagnoses})

@login_required
def diagnosis_detail(request, diagnosis_id):
    """View detailed diagnosis"""
    try:
        diagnosis = AIDiagnosis.objects.get(id=diagnosis_id, user=request.user)
        return render(request, 'medical_ai/diagnosis_detail.html', {'diagnosis': diagnosis})
    except AIDiagnosis.DoesNotExist:
        return JsonResponse({'error': 'Diagnosis not found'}, status=404)

@csrf_exempt
@require_http_methods(["POST"])
def train_model_api(request):
    """API endpoint to train the model"""
    try:
        data = json.loads(request.body)
        training_data_path = data.get('training_data_path')
        epochs = data.get('epochs', 50)
        
        if not training_data_path:
            return JsonResponse({'error': 'Training data path required'}, status=400)
        
        # Train model
        history = live_diagnosis.train_model(training_data_path, epochs)
        
        if history:
            return JsonResponse({
                'success': True,
                'message': f'Model trained successfully for {epochs} epochs',
                'final_accuracy': float(history.history['accuracy'][-1]),
                'final_val_accuracy': float(history.history['val_accuracy'][-1])
            })
        else:
            return JsonResponse({'error': 'Model training failed'}, status=500)
            
    except Exception as e:
        logger.error(f"Error in train_model_api: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def get_diagnosis_stats(request):
    """Get diagnosis statistics for user"""
    try:
        total_diagnoses = AIDiagnosis.objects.filter(user=request.user).count()
        
        # Get most common diagnoses
        from django.db.models import Count
        common_diagnoses = AIDiagnosis.objects.filter(user=request.user).values('predicted_disease').annotate(count=Count('predicted_disease')).order_by('-count')[:5]
        
        # Get recent diagnoses
        recent_diagnoses = AIDiagnosis.objects.filter(user=request.user).order_by('-created_at')[:5]
        
        stats = {
            'total_diagnoses': total_diagnoses,
            'common_diagnoses': list(common_diagnoses),
            'recent_diagnoses': [
                {
                    'id': d.id,
                    'disease': d.predicted_disease,
                    'confidence': d.confidence_score,
                    'date': d.created_at.isoformat()
                }
                for d in recent_diagnoses
            ]
        }
        
        return JsonResponse(stats)
        
    except Exception as e:
        logger.error(f"Error in get_diagnosis_stats: {e}")
        return JsonResponse({'error': str(e)}, status=500)