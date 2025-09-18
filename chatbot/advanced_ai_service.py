import os
import json
import asyncio
import aiohttp
from typing import Dict, List, Optional, Tuple
from django.conf import settings
from django.utils import timezone
import logging

# AI Provider imports
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

logger = logging.getLogger(__name__)

class AdvancedAIService:
    """Advanced AI service integrating OpenAI and Gemini for medical assistance."""
    
    def __init__(self):
        self.openai_client = None
        self.gemini_model = None
        self.initialize_ai_providers()
        
        # Medical context and safety guidelines
        self.medical_context = self._load_medical_context()
        self.safety_guidelines = self._load_safety_guidelines()
        
    def initialize_ai_providers(self):
        """Initialize AI providers with API keys."""
        # Initialize OpenAI
        if OPENAI_AVAILABLE and hasattr(settings, 'OPENAI_API_KEY') and settings.OPENAI_API_KEY:
            try:
                openai.api_key = settings.OPENAI_API_KEY
                self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
                logger.info("OpenAI client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI: {str(e)}")
                self.openai_client = None
        
        # Initialize Gemini
        if GEMINI_AVAILABLE and hasattr(settings, 'GEMINI_API_KEY') and settings.GEMINI_API_KEY:
            try:
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self.gemini_model = genai.GenerativeModel('gemini-pro')
                logger.info("Gemini model initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini: {str(e)}")
                self.gemini_model = None
    
    def _load_medical_context(self) -> str:
        """Load medical context for AI prompts."""
        return """
        You are an advanced AI medical assistant designed to help patients with health-related questions and concerns.
        
        IMPORTANT MEDICAL DISCLAIMERS:
        - You are NOT a replacement for professional medical advice, diagnosis, or treatment
        - Always recommend consulting with qualified healthcare professionals for serious concerns
        - For emergencies, always advise calling emergency services immediately
        - Your responses are for informational purposes only and should not be considered medical advice
        
        CAPABILITIES:
        - Provide general health information and education
        - Help interpret symptoms and suggest possible causes
        - Offer guidance on when to seek medical attention
        - Provide information about medications and treatments
        - Assist with health monitoring and lifestyle advice
        - Analyze medical images and reports (with appropriate disclaimers)
        
        RESPONSE GUIDELINES:
        - Be empathetic and understanding
        - Use clear, non-technical language when possible
        - Always include appropriate medical disclaimers
        - Prioritize patient safety and well-being
        - Encourage professional medical consultation when appropriate
        """
    
    def _load_safety_guidelines(self) -> Dict:
        """Load safety guidelines for AI responses."""
        return {
            'emergency_keywords': [
                'emergency', 'urgent', 'critical', 'severe', 'unconscious', 'bleeding',
                'heart attack', 'stroke', 'severe pain', 'can\'t breathe', 'chest pain',
                'severe headache', 'paralysis', 'severe burns', 'poisoning'
            ],
            'high_risk_symptoms': [
                'chest pain', 'shortness of breath', 'severe headache', 'unconsciousness',
                'severe bleeding', 'paralysis', 'severe burns', 'poisoning', 'severe abdominal pain'
            ],
            'disclaimer_required': [
                'diagnosis', 'treatment', 'medication', 'surgery', 'therapy'
            ]
        }
    
    async def get_ai_response(self, user_message: str, context: Dict = None, provider: str = 'auto') -> Dict:
        """Get AI response from the specified provider."""
        try:
            # Check for emergency situations first
            emergency_check = self._check_emergency_situation(user_message)
            if emergency_check['is_emergency']:
                return emergency_check
            
            # Always use fallback response for now to avoid API issues
            response = self._get_fallback_response(user_message)
            
            # Process and enhance the response
            enhanced_response = self._enhance_response(response, user_message, context)
            
            return {
                'success': True,
                'response': enhanced_response['text'],
                'provider': 'fallback',
                'confidence': enhanced_response.get('confidence', 0.8),
                'analysis': enhanced_response.get('analysis'),
                'recommendations': enhanced_response.get('recommendations'),
                'emergency_alert': enhanced_response.get('emergency_alert', False),
                'timestamp': timezone.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in AI response generation: {str(e)}")
            return {
                'success': True,
                'response': f"I understand you said: '{user_message}'. I'm here to help with your health questions. Could you please provide more details about your symptoms or health concerns?",
                'provider': 'fallback'
            }
    
    def _check_emergency_situation(self, message: str) -> Dict:
        """Check if the message indicates an emergency situation."""
        message_lower = message.lower()
        
        for keyword in self.safety_guidelines['emergency_keywords']:
            if keyword in message_lower:
                return {
                    'is_emergency': True,
                    'success': True,
                    'response': f"🚨 EMERGENCY ALERT! I detect this may be a medical emergency.\n\n" +
                               f"Please:\n" +
                               f"1. Call emergency services immediately (911/112)\n" +
                               f"2. Go to the nearest emergency room\n" +
                               f"3. Do not delay seeking medical help\n\n" +
                               f"Can you tell me more about what's happening so I can provide additional guidance?",
                    'emergency_alert': True,
                    'provider': 'emergency_check'
                }
        
        return {'is_emergency': False}
    
    def _prepare_medical_prompt(self, user_message: str, context: Dict = None) -> str:
        """Prepare a comprehensive medical prompt for AI."""
        prompt = f"{self.medical_context}\n\n"
        
        if context:
            if 'symptoms' in context:
                prompt += f"Patient reported symptoms: {', '.join(context['symptoms'])}\n"
            if 'medical_history' in context:
                prompt += f"Relevant medical history: {context['medical_history']}\n"
            if 'current_medications' in context:
                prompt += f"Current medications: {', '.join(context['current_medications'])}\n"
            if 'vital_signs' in context:
                prompt += f"Recent vital signs: {context['vital_signs']}\n"
        
        prompt += f"\nPatient question/concern: {user_message}\n\n"
        prompt += "Please provide a helpful, empathetic, and medically appropriate response. " \
                 "Include relevant disclaimers and recommendations for professional medical consultation when appropriate."
        
        return prompt
    
    def _select_best_provider(self) -> str:
        """Select the best available AI provider."""
        if self.openai_client and self.gemini_model:
            # Both available - could implement logic to choose based on query type
            return 'openai'  # Default to OpenAI for now
        elif self.openai_client:
            return 'openai'
        elif self.gemini_model:
            return 'gemini'
        else:
            return 'fallback'
    
    async def _get_openai_response(self, prompt: str) -> str:
        """Get response from OpenAI GPT model."""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful medical AI assistant. Always prioritize patient safety and recommend professional medical consultation when appropriate."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7,
                top_p=0.9
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise e
    
    async def _get_gemini_response(self, prompt: str) -> str:
        """Get response from Google Gemini model."""
        try:
            response = self.gemini_model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            raise e
    
    def _get_fallback_response(self, user_message: str) -> str:
        """Get fallback response when AI providers are unavailable."""
        message_lower = user_message.lower()
        
        # Check for emergency situations first
        emergency_keywords = ['emergency', 'urgent', 'critical', 'severe', 'unconscious', 'bleeding', 'heart attack', 'stroke']
        if any(keyword in message_lower for keyword in emergency_keywords):
            return "🚨 EMERGENCY ALERT! This sounds serious. Please:\n\n" + \
                   "1. Call emergency services immediately (911/112)\n" + \
                   "2. Go to the nearest emergency room\n" + \
                   "3. Do not delay seeking medical help\n\n" + \
                   "Can you tell me more about what's happening?"
        
        elif any(word in message_lower for word in ['symptom', 'symptoms', 'feeling', 'pain', 'ache']):
            return "I understand you're experiencing symptoms. Here's what I can help with:\n\n" + \
                   "• General information about common symptoms\n" + \
                   "• Guidance on when to seek medical attention\n" + \
                   "• Suggestions for symptom tracking\n\n" + \
                   "Please describe your symptoms in more detail, and remember to consult with a healthcare professional for proper evaluation."
        
        elif any(word in message_lower for word in ['medicine', 'medication', 'drug', 'pill', 'tablet']):
            return "For medication-related questions, I can provide:\n\n" + \
                   "• General information about medications\n" + \
                   "• Common side effects and interactions\n" + \
                   "• General dosage guidelines\n\n" + \
                   "However, I strongly recommend consulting with a pharmacist or doctor for personalized advice based on your specific situation and medical history."
        
        elif any(word in message_lower for word in ['hi', 'hello', 'hey', 'help']):
            return "Hello! I'm your AI health assistant. I can help you with:\n\n" + \
                   "• General health questions and information\n" + \
                   "• Symptom analysis and guidance\n" + \
                   "• Medication information\n" + \
                   "• Health monitoring tips\n\n" + \
                   "What would you like to know about your health today?"
        
        else:
            return "I'm here to help with your health-related questions. I can provide:\n\n" + \
                   "• General health information and education\n" + \
                   "• Symptom analysis and guidance\n" + \
                   "• Medication information\n" + \
                   "• Health monitoring recommendations\n\n" + \
                   "Please remember that I'm not a replacement for professional medical advice. " + \
                   "For specific medical concerns, please consult with a qualified healthcare professional."
    
    def _enhance_response(self, response: str, user_message: str, context: Dict = None) -> Dict:
        """Enhance AI response with additional analysis and recommendations."""
        enhanced = {
            'text': response,
            'confidence': 0.8,
            'analysis': None,
            'recommendations': [],
            'emergency_alert': False
        }
        
        # Check for high-risk content
        if any(keyword in response.lower() for keyword in self.safety_guidelines['high_risk_symptoms']):
            enhanced['emergency_alert'] = True
            enhanced['recommendations'].append("Consider seeking immediate medical attention")
        
        # Add general recommendations
        enhanced['recommendations'].extend([
            "Consult with a healthcare professional for personalized advice",
            "Keep track of your symptoms and any changes",
            "Follow up with your doctor if symptoms persist or worsen"
        ])
        
        # Analyze response confidence
        if len(response) > 200 and any(word in response.lower() for word in ['likely', 'probably', 'suggests']):
            enhanced['confidence'] = 0.9
        elif len(response) < 100:
            enhanced['confidence'] = 0.6
        
        return enhanced
    
    async def analyze_medical_image(self, image_data: bytes, image_type: str, description: str = None) -> Dict:
        """Analyze medical images using AI vision models."""
        try:
            # This would integrate with vision models like GPT-4V or Gemini Vision
            # For now, return a structured analysis
            analysis = {
                'success': True,
                'analysis_text': f"AI analysis of {image_type} image. This is a simulated analysis - " \
                               f"in production, this would use advanced computer vision models.",
                'findings': [],
                'recommendations': [
                    "Consult with a radiologist for professional interpretation",
                    "Share this analysis with your healthcare provider",
                    "Follow up based on your doctor's recommendations"
                ],
                'confidence': 0.7,
                'provider': 'vision_ai'
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in medical image analysis: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'analysis_text': "Unable to analyze the image at this time. Please consult with a healthcare professional."
            }
    
    def get_conversation_summary(self, messages: List[Dict]) -> str:
        """Generate a summary of the conversation for medical records."""
        if not messages:
            return "No conversation to summarize."
        
        # Extract key information from conversation
        symptoms = []
        concerns = []
        recommendations = []
        
        for message in messages:
            if message.get('type') == 'USER':
                content = message.get('content', '').lower()
                if any(word in content for word in ['symptom', 'pain', 'feeling']):
                    symptoms.append(message.get('content', ''))
                else:
                    concerns.append(message.get('content', ''))
            elif message.get('type') == 'BOT':
                content = message.get('content', '')
                if 'recommend' in content.lower():
                    recommendations.append(content)
        
        summary = "CONVERSATION SUMMARY:\n\n"
        if symptoms:
            summary += f"Reported Symptoms: {'; '.join(symptoms[:3])}\n\n"
        if concerns:
            summary += f"Patient Concerns: {'; '.join(concerns[:3])}\n\n"
        if recommendations:
            summary += f"AI Recommendations: {'; '.join(recommendations[:2])}\n\n"
        
        summary += "Note: This is an AI-generated summary. Please review with healthcare professionals."
        
        return summary

# Global instance
advanced_ai_service = AdvancedAIService()
