from django.db import models
from accounts.models import User
from hospitals.models import Doctor, HospitalProfile
from django.utils import timezone
import uuid

class Appointment(models.Model):
    """Model for appointments between patients and doctors."""
    APPOINTMENT_STATUS = (
        ('REQUESTED', 'Requested'),
        ('CONFIRMED', 'Confirmed'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('RESCHEDULED', 'Rescheduled'),
        ('NO_SHOW', 'No Show'),
    )
    
    APPOINTMENT_TYPE = (
        ('PHYSICAL', 'Physical Visit'),
        ('VIDEO', 'Video Consultation'),
        ('HOME', 'Home Visit'),
    )
    
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patient_appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='doctor_appointments')
    appointment_type = models.CharField(max_length=10, choices=APPOINTMENT_TYPE)
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    status = models.CharField(max_length=15, choices=APPOINTMENT_STATUS, default='REQUESTED')
    token_number = models.PositiveIntegerField(blank=True, null=True)
    reason_for_visit = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    # Home visit specific fields
    address = models.TextField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    
    # For videocall appointments
    meeting_id = models.CharField(max_length=50, blank=True, null=True, unique=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.patient.profile.full_name if hasattr(self.patient, 'profile') else self.patient.phone_number} - Dr. {self.doctor.name} ({self.appointment_date})"
    
    def save(self, *args, **kwargs):
        # Generate meeting ID for video appointments
        if self.appointment_type == 'VIDEO' and not self.meeting_id:
            self.meeting_id = str(uuid.uuid4())
        
        # Generate token number if not provided
        if not self.token_number and self.status == 'CONFIRMED':
            # Get the count of confirmed appointments for the same doctor, date, and time
            same_time_appointments = Appointment.objects.filter(
                doctor=self.doctor,
                appointment_date=self.appointment_date,
                status='CONFIRMED'
            ).count()
            
            self.token_number = same_time_appointments + 1
            
        super().save(*args, **kwargs)
    
    def is_upcoming(self):
        appointment_datetime = timezone.datetime.combine(
            self.appointment_date, 
            self.appointment_time,
            tzinfo=timezone.get_current_timezone()
        )
        return appointment_datetime > timezone.now()

class MedicalRecord(models.Model):
    """Medical records for patients created after appointments."""
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='medical_record')
    diagnosis = models.TextField()
    symptoms = models.TextField(blank=True, null=True)
    prescriptions = models.TextField(blank=True, null=True)
    follow_up_date = models.DateField(blank=True, null=True)
    additional_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Medical Record - {self.appointment}"

class VideoSession(models.Model):
    """Details for video consultation sessions."""
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='video_session')
    meeting_id = models.CharField(max_length=50, unique=True)
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    session_recording_url = models.URLField(blank=True, null=True)
    
    def __str__(self):
        return f"Video Session for {self.appointment}"
    
    def save(self, *args, **kwargs):
        if not self.meeting_id and self.appointment.meeting_id:
            self.meeting_id = self.appointment.meeting_id
        super().save(*args, **kwargs)
    
    def duration_in_minutes(self):
        if self.start_time and self.end_time:
            duration = self.end_time - self.start_time
            return int(duration.total_seconds() / 60)
        return 0

class PatientMedicalHistory(models.Model):
    """Complete medical history record for patients."""
    patient = models.OneToOneField(User, on_delete=models.CASCADE, related_name='medical_history')
    chronic_diseases = models.TextField(blank=True, null=True)
    allergies = models.TextField(blank=True, null=True)
    surgeries = models.TextField(blank=True, null=True)
    family_medical_history = models.TextField(blank=True, null=True)
    current_medications = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Patient Medical Histories"
    
    def __str__(self):
        return f"Medical History of {self.patient.profile.full_name if hasattr(self.patient, 'profile') else self.patient.phone_number}"

class Prescription(models.Model):
    """Detailed prescriptions for patients."""
    medical_record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE, related_name='detailed_prescriptions')
    medicine_name = models.CharField(max_length=255)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)
    duration = models.CharField(max_length=100)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.medicine_name} - {self.medical_record.appointment}"

class QueueToken(models.Model):
    """Model for managing real-time queue tokens in hospitals."""
    TOKEN_STATUS = (
        ('WAITING', 'Waiting'),
        ('CALLING', 'Calling'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    )
    
    token_number = models.PositiveIntegerField()
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='queue_tokens')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='queue_tokens')
    hospital = models.ForeignKey(HospitalProfile, on_delete=models.CASCADE, related_name='queue_tokens')
    department = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=15, choices=TOKEN_STATUS, default='WAITING')
    estimated_wait_time = models.PositiveIntegerField(help_text='Estimated wait time in minutes', blank=True, null=True)
    priority = models.CharField(max_length=20, choices=[
        ('NORMAL', 'Normal'),
        ('URGENT', 'Urgent'),
        ('EMERGENCY', 'Emergency')
    ], default='NORMAL')
    reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    called_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-priority', 'created_at']
        unique_together = ['token_number', 'hospital', 'created_at']
    
    def __str__(self):
        return f"Token #{self.token_number} - {self.patient.profile.full_name if hasattr(self.patient, 'profile') else self.patient.phone_number} - {self.hospital.name}"
    
    def save(self, *args, **kwargs):
        if not self.token_number:
            # Generate next token number for the hospital
            last_token = QueueToken.objects.filter(
                hospital=self.hospital,
                created_at__date=self.created_at.date() if self.created_at else timezone.now().date()
            ).order_by('-token_number').first()
            
            if last_token:
                self.token_number = last_token.token_number + 1
            else:
                self.token_number = 1
        
        super().save(*args, **kwargs)
    
    def get_wait_time(self):
        """Calculate actual wait time in minutes."""
        if self.called_at and self.created_at:
            wait_time = self.called_at - self.created_at
            return int(wait_time.total_seconds() / 60)
        return 0
    
    def get_position_in_queue(self):
        """Get current position in the queue."""
        if self.status == 'WAITING':
            return QueueToken.objects.filter(
                hospital=self.hospital,
                doctor=self.doctor,
                status='WAITING',
                created_at__lt=self.created_at
            ).count() + 1
        return 0
