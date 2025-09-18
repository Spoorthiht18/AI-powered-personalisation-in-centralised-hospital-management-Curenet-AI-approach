from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, logout
from django.utils import timezone
import json
import random
import string
import logging
from ..models import User, OTP, UserProfile, PatientProfile
from ..services import sms_service

# Set up logging
logger = logging.getLogger(__name__)

@csrf_exempt
def login_api(request):
    """API endpoint for user login."""
    if request.method == 'POST':
        # This would handle API login in a real app
        return JsonResponse({
            'success': True,
            'message': 'Login successful',
            'redirect_url': '/accounts/dashboard/'
        })
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def logout_api(request):
    """API endpoint for user logout."""
    if request.method == 'POST':
        logout(request)
        return JsonResponse({
            'success': True,
            'message': 'Logout successful'
        })
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def send_otp_api(request):
    """API endpoint to send OTP to user's phone."""
    if request.method == 'POST':
        try:
            # Log the raw request
            logger.info(f"OTP API request received: {request.body}")
            print(f"OTP API request received: {request.body}")
            
            # For debug - check content type
            print(f"Content-Type: {request.content_type}")
            
            # Try to parse JSON
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError as e:
                print(f"JSON parse error: {e}")
                # Fallback to form data
                data = request.POST
                
            phone_number = data.get('phone_number')
            user_type = data.get('user_type', 'PATIENT')
            
            print(f"Extracted phone: {phone_number}, type: {user_type}")
            
            if not phone_number:
                error_msg = 'Phone number is required'
                print(error_msg)
                return JsonResponse({'success': False, 'message': error_msg}, status=400)
                
            # Get or create user
            try:
                user, created = User.objects.get_or_create(
                    phone_number=phone_number,
                    defaults={'user_type': user_type}
                )
                print(f"User {'created' if created else 'found'}: {user}")
            except Exception as user_error:
                error_msg = f"User error: {str(user_error)}"
                print(error_msg)
                return JsonResponse({'success': False, 'message': error_msg}, status=500)
            
            # Generate OTP
            otp_code = ''.join(random.choices(string.digits, k=6))
            print(f"Generated OTP: {otp_code}")
            
            # Save OTP in database
            try:
                otp = OTP(user=user, otp_code=otp_code)
                otp.save()
                print(f"OTP saved: {otp}")
            except Exception as otp_error:
                error_msg = f"OTP save error: {str(otp_error)}"
                print(error_msg)
                return JsonResponse({'success': False, 'message': error_msg}, status=500)
            
            # Send OTP via SMS
            sms_result = sms_service.send_otp(phone_number, otp_code)
            
            if sms_result['success']:
                response_data = {
                    'success': True,
                    'message': f"OTP sent successfully via {sms_result['method']}",
                    'method': sms_result['method']
                }
                
                # Include debug OTP for console mode (development only)
                if sms_result['method'] == 'console':
                    response_data['debug_otp'] = otp_code
                    
                return JsonResponse(response_data)
            else:
                return JsonResponse({
                    'success': False,
                    'message': sms_result['message']
                }, status=500)
                
        except Exception as e:
            error_msg = f"Error sending OTP: {str(e)}"
            print(error_msg)
            logger.error(error_msg)
            return JsonResponse({'success': False, 'message': error_msg}, status=500)
            
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def verify_otp_api(request):
    """API endpoint to verify OTP."""
    if request.method == 'POST':
        try:
            # Log the raw request
            print(f"Verify OTP request received: {request.body}")
            
            # Try to parse JSON
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                # Fallback to form data
                data = request.POST
                
            phone_number = data.get('phone_number')
            otp_code = data.get('otp_code')
            
            print(f"Verifying OTP - Phone: {phone_number}, OTP: {otp_code}")
            
            if not phone_number or not otp_code:
                error_msg = 'Phone number and OTP are required'
                print(error_msg)
                return JsonResponse({'success': False, 'message': error_msg}, status=400)
                
            # Find user by phone
            try:
                user = User.objects.get(phone_number=phone_number)
                print(f"User found: {user}")
            except User.DoesNotExist:
                error_msg = 'User not found'
                print(error_msg)
                return JsonResponse({'success': False, 'message': error_msg}, status=404)
                
            # Get the latest OTP for this user
            try:
                otp = OTP.objects.filter(user=user).order_by('-created_at').first()
                
                if not otp:
                    error_msg = 'No OTP found'
                    print(error_msg)
                    return JsonResponse({'success': False, 'message': error_msg}, status=404)
                
                print(f"Found OTP: {otp.otp_code}, expired: {otp.is_expired()}")
                
                if otp.is_expired():
                    error_msg = 'OTP has expired'
                    print(error_msg)
                    return JsonResponse({'success': False, 'message': error_msg}, status=400)
                    
                if otp.otp_code != otp_code:
                    error_msg = 'Invalid OTP'
                    print(error_msg)
                    return JsonResponse({'success': False, 'message': error_msg}, status=400)
                    
                # Mark OTP as verified
                otp.is_verified = True
                otp.save()
                print("OTP verified successfully")
                
                # Log the user in
                login(request, user)
                
                return JsonResponse({
                    'success': True,
                    'message': 'OTP verified successfully',
                    'redirect_url': '/accounts/dashboard/'
                })
            except Exception as e:
                error_msg = f"Error verifying OTP: {str(e)}"
                print(error_msg)
                return JsonResponse({'success': False, 'message': error_msg}, status=500)
                
        except Exception as e:
            error_msg = f"Error in OTP verification: {str(e)}"
            print(error_msg)
            return JsonResponse({'success': False, 'message': error_msg}, status=500)
            
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def profile_api(request):
    """API endpoint to get user profile."""
    if request.method == 'GET':
        # This would return profile in a real app
        return JsonResponse({
            'success': True,
            'profile': {
                'full_name': 'Demo User',
                'email': 'demo@example.com',
                'phone_number': '1234567890',
            }
        })
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def update_profile_api(request):
    """API endpoint to update user profile."""
    if request.method == 'POST':
        # This would update profile in a real app
        return JsonResponse({
            'success': True,
            'message': 'Profile updated successfully'
        })
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def update_patient_profile_api(request):
    """API endpoint to update patient profile."""
    if request.method == 'POST':
        # This would update patient profile in a real app
        return JsonResponse({
            'success': True,
            'message': 'Patient profile updated successfully'
        })
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def register_api(request):
    """API endpoint for user registration."""
    if request.method == 'POST':
        # This would handle registration in a real app
        return JsonResponse({
            'success': True,
            'message': 'Registration successful',
            'redirect_url': '/accounts/login/'
        })
    return JsonResponse({'error': 'Invalid request'}, status=400) 