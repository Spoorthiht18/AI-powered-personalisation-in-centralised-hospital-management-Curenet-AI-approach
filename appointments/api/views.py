from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
import json
from ..models import Appointment, MedicalRecord, VideoSession, PatientMedicalHistory, Prescription, QueueToken
from hospitals.models import HospitalProfile, Doctor

@csrf_exempt
def appointment_list_api(request):
    """API endpoint to list appointments."""
    appointments = []  # This would fetch real appointments in a real app
    return JsonResponse({'appointments': appointments})

@csrf_exempt
def create_appointment_api(request):
    """API endpoint to create an appointment."""
    if request.method == 'POST':
        # This would create an appointment in a real app
        return JsonResponse({
            'success': True,
            'appointment_id': 1,  # Placeholder ID
            'message': 'Appointment created successfully'
        })
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def appointment_detail_api(request, appointment_id):
    """API endpoint to get appointment details."""
    # This would fetch a real appointment in a real app
    appointment = {
        'id': appointment_id,
        'doctor': 'Dr. Demo',
        'date': '2023-06-01',
        'time': '10:00 AM',
        'status': 'CONFIRMED',
        'token_number': 5,
    }
    return JsonResponse({'appointment': appointment})

@csrf_exempt
def cancel_appointment_api(request, appointment_id):
    """API endpoint to cancel an appointment."""
    if request.method == 'POST':
        # This would cancel the appointment in a real app
        return JsonResponse({
            'success': True,
            'message': 'Appointment cancelled successfully'
        })
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def reschedule_appointment_api(request, appointment_id):
    """API endpoint to reschedule an appointment."""
    if request.method == 'POST':
        # This would reschedule the appointment in a real app
        return JsonResponse({
            'success': True,
            'message': 'Appointment rescheduled successfully'
        })
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def medical_record_list_api(request):
    """API endpoint to list medical records."""
    records = []  # This would fetch real records in a real app
    return JsonResponse({'records': records})

@csrf_exempt
def medical_record_detail_api(request, record_id):
    """API endpoint to get medical record details."""
    # This would fetch a real record in a real app
    record = {
        'id': record_id,
        'doctor': 'Dr. Demo',
        'diagnosis': 'Common Cold',
        'prescriptions': ['Paracetamol', 'Vitamin C'],
        'date': '2023-06-01',
    }
    return JsonResponse({'record': record})

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def create_queue_token_api(request):
    """API endpoint to create a new queue token."""
    try:
        data = json.loads(request.body)
        hospital_id = data.get('hospital_id')
        doctor_id = data.get('doctor_id')
        reason = data.get('reason', 'General consultation')
        
        if not hospital_id or not doctor_id:
            return JsonResponse({
                'error': 'Hospital ID and Doctor ID are required'
            }, status=400)
        
        # Check if user already has an active token for this doctor
        existing_token = QueueToken.objects.filter(
            patient=request.user,
            doctor_id=doctor_id,
            status__in=['WAITING', 'CALLING', 'IN_PROGRESS']
        ).first()
        
        if existing_token:
            return JsonResponse({
                'error': 'You already have an active token for this doctor'
            }, status=400)
        
        # Create new token
        token = QueueToken.objects.create(
            patient=request.user,
            doctor_id=doctor_id,
            hospital_id=hospital_id,
            reason=reason,
            estimated_wait_time=15  # Default 15 minutes
        )
        
        return JsonResponse({
            'success': True,
            'token_number': token.token_number,
            'estimated_wait_time': token.estimated_wait_time,
            'message': 'Token created successfully'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)

@csrf_exempt
@login_required
def get_user_tokens_api(request):
    """API endpoint to get user's active queue tokens."""
    try:
        tokens = QueueToken.objects.filter(
            patient=request.user,
            status__in=['WAITING', 'CALLING', 'IN_PROGRESS']
        ).select_related('doctor', 'hospital').order_by('created_at')
        
        token_list = []
        for token in tokens:
            token_list.append({
                'id': token.id,
                'token_number': token.token_number,
                'hospital_name': token.hospital.name,
                'doctor_name': token.doctor.name,
                'department': token.department or token.doctor.specialization,
                'status': token.status,
                'priority': token.priority,
                'created_at': token.created_at.isoformat(),
                'estimated_wait_time': token.estimated_wait_time,
                'position': token.get_position_in_queue()
            })
        
        return JsonResponse({
            'success': True,
            'tokens': token_list
        })
        
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)

@csrf_exempt
@login_required
def cancel_queue_token_api(request, token_id):
    """API endpoint to cancel a queue token."""
    try:
        token = QueueToken.objects.get(
            id=token_id,
            patient=request.user
        )
        
        if token.status in ['COMPLETED', 'CANCELLED']:
            return JsonResponse({
                'error': 'Cannot cancel completed or already cancelled token'
            }, status=400)
        
        token.status = 'CANCELLED'
        token.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Token cancelled successfully'
        })
        
    except QueueToken.DoesNotExist:
        return JsonResponse({
            'error': 'Token not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500) 