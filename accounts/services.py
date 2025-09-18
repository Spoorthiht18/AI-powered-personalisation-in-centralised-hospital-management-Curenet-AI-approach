import os
import logging
from django.conf import settings
from twilio.rest import Client
from twilio.base.exceptions import TwilioException

logger = logging.getLogger(__name__)

class SMSService:
    """Service class for sending SMS messages using Twilio."""
    
    def __init__(self):
        self.account_sid = settings.TWILIO_ACCOUNT_SID
        self.auth_token = settings.TWILIO_AUTH_TOKEN
        self.phone_number = settings.TWILIO_PHONE_NUMBER
        
        # Initialize Twilio client if credentials are available
        if all([self.account_sid, self.auth_token, self.phone_number]):
            try:
                self.client = Client(self.account_sid, self.auth_token)
                self.is_available = True
                logger.info("Twilio SMS service initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Twilio client: {e}")
                self.is_available = False
        else:
            self.is_available = False
            logger.warning("Twilio credentials not configured, SMS service unavailable")
    
    def send_otp(self, phone_number, otp_code):
        """
        Send OTP via SMS.
        
        Args:
            phone_number (str): Recipient's phone number
            otp_code (str): 6-digit OTP code
            
        Returns:
            dict: Result with success status and message
        """
        if not self.is_available:
            # Fallback to console logging for development
            logger.info(f"OTP for {phone_number}: {otp_code}")
            return {
                'success': True,
                'message': 'OTP sent successfully (console mode)',
                'method': 'console'
            }
        
        try:
            # Format phone number (ensure it starts with +)
            if not phone_number.startswith('+'):
                # Assuming Indian numbers, add +91
                if phone_number.startswith('0'):
                    phone_number = '+91' + phone_number[1:]
                elif len(phone_number) == 10:
                    phone_number = '+91' + phone_number
                else:
                    phone_number = '+' + phone_number
            
            # Create message
            message_body = f"Your CureNet AI verification code is: {otp_code}. Valid for 10 minutes. Do not share this code with anyone."
            
            # Send SMS via Twilio
            message = self.client.messages.create(
                body=message_body,
                from_=self.phone_number,
                to=phone_number
            )
            
            logger.info(f"SMS sent successfully to {phone_number}. SID: {message.sid}")
            
            return {
                'success': True,
                'message': 'OTP sent successfully via SMS',
                'method': 'sms',
                'message_sid': message.sid
            }
            
        except TwilioException as e:
            error_msg = f"Twilio SMS error: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'message': 'Failed to send SMS. Please try again.',
                'error': str(e),
                'method': 'sms'
            }
            
        except Exception as e:
            error_msg = f"Unexpected error sending SMS: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'message': 'An error occurred while sending SMS.',
                'error': str(e),
                'method': 'sms'
            }
    
    def send_welcome_message(self, phone_number, user_name):
        """Send welcome message after successful registration."""
        if not self.is_available:
            logger.info(f"Welcome message for {phone_number}: Welcome {user_name} to CureNet AI!")
            return {'success': True, 'message': 'Welcome message sent (console mode)'}
        
        try:
            if not phone_number.startswith('+'):
                if phone_number.startswith('0'):
                    phone_number = '+91' + phone_number[1:]
                elif len(phone_number) == 10:
                    phone_number = '+91' + phone_number
                else:
                    phone_number = '+' + phone_number
            
            message_body = f"Welcome {user_name} to CureNet AI! Your account has been successfully created. We're here to help you with your healthcare needs."
            
            message = self.client.messages.create(
                body=message_body,
                from_=self.phone_number,
                to=phone_number
            )
            
            logger.info(f"Welcome SMS sent to {phone_number}")
            return {'success': True, 'message': 'Welcome message sent successfully'}
            
        except Exception as e:
            logger.error(f"Failed to send welcome message: {e}")
            return {'success': False, 'message': 'Failed to send welcome message'}

# Global instance
sms_service = SMSService()
