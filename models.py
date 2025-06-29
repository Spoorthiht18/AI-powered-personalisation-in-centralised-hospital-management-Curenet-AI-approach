from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import random
import string
import logging

# Set up logging
logger = logging.getLogger(__name__)

class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    def _create_user(self, phone_number, password=None, **extra_fields):
        """Create and save a User with the given phone number and password."""
        if not phone_number:
            raise ValueError('The phone number must be set')
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone_number, password=None, **extra_fields):
        """Create and save a regular User with the given phone number and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(phone_number, password, **extra_fields)

    def create_superuser(self, phone_number, password, **extra_fields):
        """Create and save a SuperUser with the given phone number and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', 'ADMIN')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(phone_number, password, **extra_fields)

class User(AbstractUser):
    """Custom User model with phone number as the unique identifier."""
    USER_TYPE_CHOICES = (
        ('PATIENT', 'Patient'),
        ('HOSPITAL', 'Hospital'),
        ('ADMIN', 'Admin'),
    )
    
    username = None
    phone_number = models.CharField(_('phone number'), max_length=15, unique=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='PATIENT')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return f"{self.phone_number} - {self.get_user_type_display()}"

class OTP(models.Model):
    """Model to store OTP for phone verification."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otps')
    otp_code = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "OTP"
        verbose_name_plural = "OTPs"

    def __str__(self):
        return f"{self.user.phone_number} - {self.otp_code}"
    
    def save(self, *args, **kwargs):
        try:
            # Generate OTP if not provided
            if not self.otp_code:
                self.otp_code = ''.join(random.choices(string.digits, k=6))
                logger.info(f"Generated new OTP for {self.user.phone_number}")
            
            # Set expiry time if not provided
            if not self.expires_at:
                from django.conf import settings
                expiry_time = getattr(settings, 'OTP_EXPIRY_TIME', 10 * 60)  # Default: 10 minutes
                self.expires_at = timezone.now() + timezone.timedelta(seconds=expiry_time)
                logger.info(f"Set expiry time for OTP: {self.expires_at}")
                
            logger.info(f"Saving OTP for {self.user.phone_number}: {self.otp_code}")
            super().save(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error saving OTP: {e}")
            raise
    
    def is_expired(self):
        """Check if the OTP has expired."""
        if not self.expires_at:
            # If no expiry time is set, consider it expired for safety
            return True
        return timezone.now() > self.expires_at

class UserProfile(models.Model):
    """Extended profile information for all users."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    
    def __str__(self):
        return f"Profile of {self.user.phone_number}"

class PatientProfile(models.Model):
    """Additional profile information specific to patients."""
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    blood_group = models.CharField(max_length=5, blank=True, null=True)
    emergency_contact = models.CharField(max_length=15, blank=True, null=True)
    allergies = models.TextField(blank=True, null=True)
    chronic_diseases = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Patient Profile of {self.user.phone_number}"
    
    def calculate_age(self):
        if self.date_of_birth:
            today = timezone.now().date()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None
