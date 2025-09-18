from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import User, OTP, UserProfile, PatientProfile
import random
import string
from .services import sms_service

# Authentication views
def login_view(request):
    """Handle login page display and form submission."""
    if request.method == 'POST':
        # This would actually handle the login logic in a real app
        pass
    return render(request, 'accounts/login.html')

def logout_view(request):
    """Handle user logout."""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

def send_otp(request):
    """Send OTP to user's phone number."""
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        user_type = request.POST.get('user_type', 'PATIENT')
        
        if not phone_number:
            messages.error(request, 'Phone number is required')
            return render(request, 'accounts/login.html')
            
        # Get or create user
        user, created = User.objects.get_or_create(
            phone_number=phone_number,
            defaults={'user_type': user_type}
        )
        
        # Generate OTP
        otp_code = ''.join(random.choices(string.digits, k=6))
        
        # Save OTP in database
        otp = OTP(user=user, otp_code=otp_code)
        otp.save()
        
        # Send OTP via SMS
        sms_result = sms_service.send_otp(phone_number, otp_code)
        
        if sms_result['success']:
            messages.success(request, f"OTP sent successfully via {sms_result['method']}")
            if sms_result['method'] == 'console':
                messages.info(request, f'For development: OTP is {otp_code}')
        else:
            messages.error(request, sms_result['message'])
        
    return render(request, 'accounts/login.html')

def verify_otp(request):
    """Verify OTP entered by user."""
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        otp_code = request.POST.get('otp_code')
        
        if not phone_number or not otp_code:
            messages.error(request, 'Phone number and OTP are required')
            return render(request, 'accounts/login.html')
            
        # Find user by phone
        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            messages.error(request, 'User not found')
            return render(request, 'accounts/login.html')
            
        # Get the latest OTP for this user
        otp = OTP.objects.filter(user=user).order_by('-created_at').first()
        
        if not otp:
            messages.error(request, 'No OTP found')
            return render(request, 'accounts/login.html')
        
        if otp.is_expired():
            messages.error(request, 'OTP has expired')
            return render(request, 'accounts/login.html')
            
        if otp.otp_code != otp_code:
            messages.error(request, 'Invalid OTP')
            return render(request, 'accounts/login.html')
            
        # Mark OTP as verified
        otp.is_verified = True
        otp.save()
        
        # Log the user in
        login(request, user)
        
        messages.success(request, 'Login successful')
        return redirect('accounts:dashboard')
        
    return render(request, 'accounts/login.html')

# Profile views
@login_required
def profile_view(request):
    """Display user profile."""
    user = request.user
    context = {
        'user': user,
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def edit_profile(request):
    """Edit basic user profile."""
    if request.method == 'POST':
        # This would actually update the profile in a real app
        pass
    return render(request, 'accounts/edit_profile.html')

@login_required
def edit_patient_profile(request):
    """Edit patient-specific profile."""
    if request.method == 'POST':
        # This would actually update the patient profile in a real app
        pass
    return render(request, 'accounts/edit_patient_profile.html')

# Dashboard view
@login_required
def dashboard(request):
    """Display user dashboard based on user type."""
    user = request.user
    
    # Example data that would be fetched in a real app
    context = {
        'user': user,
        'upcoming_appointments': [],
        'nearby_hospitals': [],
        'recent_records': [],
    }
    
    return render(request, 'accounts/dashboard.html', context)
