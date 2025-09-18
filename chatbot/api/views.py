from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import json
import uuid
from ..models import ChatSession, ChatMessage, Symptom, Disease, PatientSymptom, AIRecommendation, MedicineInfo

@csrf_exempt
def start_chat_session_api(request):
    """API endpoint to start a new chat session."""
    if request.method == 'POST':
        # This would create a new session in a real app
        session_id = str(uuid.uuid4())
        return JsonResponse({
            'success': True,
            'session_id': session_id
        })
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def end_chat_session_api(request, session_id):
    """API endpoint to end a chat session."""
    if request.method == 'POST':
        # This would end the session in a real app
        return JsonResponse({
            'success': True,
            'message': 'Chat session ended successfully'
        })
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def send_message_api(request):
    """API endpoint to send a message to the chatbot."""
    if request.method == 'POST':
        # This would process the message in a real app
        data = json.loads(request.body)
        message = data.get('message', '')
        session_id = data.get('session_id', '')
        
        # Demo response
        response = {
            'message': f"This is a demo response to: {message}",
            'timestamp': timezone.now().strftime('%H:%M')
        }
        
        return JsonResponse({
            'success': True,
            'response': response
        })
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def chat_sessions_api(request):
    """API endpoint to list chat sessions."""
    sessions = []  # This would fetch real sessions in a real app
    return JsonResponse({'sessions': sessions})

@csrf_exempt
def chat_session_detail_api(request, session_id):
    """API endpoint to get chat session details."""
    # This would fetch a real session in a real app
    session = {
        'id': session_id,
        'started_at': '2023-06-01 10:00 AM',
        'is_active': True,
    }
    return JsonResponse({'session': session})

@csrf_exempt
def chat_messages_api(request, session_id):
    """API endpoint to get messages for a chat session."""
    messages = []  # This would fetch real messages in a real app
    return JsonResponse({'messages': messages})

@csrf_exempt
def report_symptom_api(request):
    """API endpoint to report a symptom."""
    if request.method == 'POST':
        # This would save the symptom in a real app
        return JsonResponse({
            'success': True,
            'message': 'Symptom reported successfully'
        })
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def symptoms_list_api(request):
    """API endpoint to list symptoms."""
    symptoms = []  # This would fetch real symptoms in a real app
    return JsonResponse({'symptoms': symptoms})

@csrf_exempt
def recommendations_api(request, session_id):
    """API endpoint to get recommendations for a chat session."""
    recommendations = []  # This would fetch real recommendations in a real app
    return JsonResponse({'recommendations': recommendations})

@csrf_exempt
def search_medicines_api(request):
    """API endpoint to search medicines."""
    query = request.GET.get('query', '')
    medicines = []  # This would search for medicines in a real app
    return JsonResponse({'medicines': medicines, 'query': query})

@csrf_exempt
def medicine_detail_api(request, medicine_id):
    """API endpoint to get medicine details."""
    # This would fetch a real medicine in a real app
    medicine = {
        'id': medicine_id,
        'name': 'Demo Medicine',
        'usage': 'For relief from symptoms',
        'dosage': '1 tablet twice daily',
    }
    return JsonResponse({'medicine': medicine})

@csrf_exempt
def search_diseases_api(request):
    """API endpoint to search diseases."""
    query = request.GET.get('query', '')
    diseases = []  # This would search for diseases in a real app
    return JsonResponse({'diseases': diseases, 'query': query})

@csrf_exempt
def disease_detail_api(request, disease_id):
    """API endpoint to get disease details."""
    # This would fetch a real disease in a real app
    disease = {
        'id': disease_id,
        'name': 'Demo Disease',
        'description': 'A common condition',
        'symptoms': ['Fever', 'Fatigue'],
    }
    return JsonResponse({'disease': disease}) 