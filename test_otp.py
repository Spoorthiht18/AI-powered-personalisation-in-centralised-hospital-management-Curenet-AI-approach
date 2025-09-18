import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'curenet_ai.settings')
django.setup()

from accounts.models import User, OTP
import random
import string

def create_test_otp():
    # Get or create a test user
    phone_number = "9876543210"  # Test phone number
    user, created = User.objects.get_or_create(
        phone_number=phone_number,
        defaults={'user_type': 'PATIENT'}
    )
    
    if created:
        print(f"Created new test user with phone {phone_number}")
    else:
        print(f"Using existing user with phone {phone_number}")
    
    # Generate OTP manually
    otp_code = ''.join(random.choices(string.digits, k=6))
    print(f"Generated OTP code: {otp_code}")
    
    # Try to save OTP to database
    try:
        otp = OTP(user=user, otp_code=otp_code)
        otp.save()
        print(f"OTP saved successfully: {otp}")
        print(f"OTP expiry time: {otp.expires_at}")
        return True
    except Exception as e:
        print(f"Error saving OTP: {str(e)}")
        return False

if __name__ == "__main__":
    print("Starting OTP test...")
    success = create_test_otp()
    print(f"OTP test {'successful' if success else 'failed'}")
    
    # Print all OTPs in the database
    print("\nAll OTPs in database:")
    for otp in OTP.objects.all():
        print(f"- {otp} (verified: {otp.is_verified}, expired: {otp.is_expired()})") 