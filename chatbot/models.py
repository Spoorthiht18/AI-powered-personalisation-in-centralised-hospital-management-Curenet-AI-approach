from django.db import models
from accounts.models import User
from hospitals.models import Doctor, Specialization, HospitalProfile
from django.utils import timezone

class ChatSession(models.Model):
    """Represents a chat session between a user and the AI chatbot."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions')
    session_id = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"Chat Session - {self.user.phone_number} ({self.started_at})"
    
    def end_session(self):
        self.is_active = False
        self.ended_at = timezone.now()
        self.save()
    
    def duration_in_minutes(self):
        if self.ended_at:
            duration = self.ended_at - self.started_at
            return int(duration.total_seconds() / 60)
        return None

class ChatMessage(models.Model):
    """Individual messages in a chat session."""
    MESSAGE_TYPE = (
        ('USER', 'User Message'),
        ('BOT', 'Bot Message'),
    )
    
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    message_type = models.CharField(max_length=4, choices=MESSAGE_TYPE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.get_message_type_display()} in {self.session} at {self.timestamp}"

class MedicalImage(models.Model):
    """Medical images uploaded by users for AI analysis."""
    IMAGE_TYPE = (
        ('XRAY', 'X-Ray'),
        ('MRI', 'MRI Scan'),
        ('CT', 'CT Scan'),
        ('ULTRASOUND', 'Ultrasound'),
        ('BLOOD_REPORT', 'Blood Report'),
        ('PATHOLOGY', 'Pathology Report'),
        ('ECG', 'ECG Report'),
        ('OTHER', 'Other Medical Report'),
    )
    
    chat_session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='medical_images')
    image = models.ImageField(upload_to='medical_images/')
    image_type = models.CharField(max_length=20, choices=IMAGE_TYPE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.get_image_type_display()} uploaded by {self.chat_session.user.phone_number}"

class ImageAnalysis(models.Model):
    """AI analysis results of medical images."""
    medical_image = models.OneToOneField(MedicalImage, on_delete=models.CASCADE, related_name='analysis')
    analysis_text = models.TextField()
    detected_conditions = models.JSONField(default=list, help_text="List of detected medical conditions")
    confidence_score = models.FloatField(default=0.0, help_text="AI confidence in the analysis (0-1)")
    recommendations = models.TextField(blank=True, null=True)
    analyzed_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Analysis of {self.medical_image.get_image_type_display()} - Confidence: {self.confidence_score}"

class Symptom(models.Model):
    """Symptom data for AI diagnosis."""
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    related_specializations = models.ManyToManyField(Specialization, related_name='symptoms')
    severity_level = models.PositiveSmallIntegerField(default=1, help_text="1-5 scale, 5 being most severe")
    
    def __str__(self):
        return self.name

class Disease(models.Model):
    """Disease data for AI diagnosis."""
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    symptoms = models.ManyToManyField(Symptom, related_name='diseases', through='DiseaseSymptom')
    specializations = models.ManyToManyField(Specialization, related_name='diseases')
    
    def __str__(self):
        return self.name

class DiseaseSymptom(models.Model):
    """Relationship between diseases and symptoms with correlation strength."""
    disease = models.ForeignKey(Disease, on_delete=models.CASCADE)
    symptom = models.ForeignKey(Symptom, on_delete=models.CASCADE)
    correlation_strength = models.FloatField(default=0.5, help_text="Between 0 and 1, 1 being strongest")
    
    class Meta:
        unique_together = ('disease', 'symptom')
    
    def __str__(self):
        return f"{self.disease.name} - {self.symptom.name} ({self.correlation_strength})"

class PatientSymptom(models.Model):
    """Symptoms reported by patients in chat sessions."""
    chat_session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='reported_symptoms')
    symptom = models.ForeignKey(Symptom, on_delete=models.CASCADE)
    reported_at = models.DateTimeField(auto_now_add=True)
    severity_reported = models.PositiveSmallIntegerField(default=3, help_text="1-5 scale, 5 being most severe")
    
    class Meta:
        unique_together = ('chat_session', 'symptom')
    
    def __str__(self):
        return f"{self.symptom.name} reported by {self.chat_session.user.phone_number}"

class AIRecommendation(models.Model):
    """Recommendation provided by the AI based on patient symptoms."""
    RECOMMENDATION_TYPE = (
        ('DOCTOR', 'Doctor Recommendation'),
        ('HOSPITAL', 'Hospital Recommendation'),
        ('EMERGENCY', 'Emergency Advice'),
        ('SELF_CARE', 'Self Care Advice'),
        ('MEDICATION', 'Medication Information'),
    )
    
    chat_session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='ai_recommendations')
    recommendation_type = models.CharField(max_length=15, choices=RECOMMENDATION_TYPE)
    content = models.TextField()
    confidence_score = models.FloatField(default=0.0, help_text="Between 0 and 1, 1 being most confident")
    
    # Recommendations can reference specific entities
    recommended_doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True)
    recommended_hospital = models.ForeignKey(HospitalProfile, on_delete=models.SET_NULL, null=True, blank=True)
    recommended_specialization = models.ForeignKey(Specialization, on_delete=models.SET_NULL, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.get_recommendation_type_display()} for {self.chat_session.user.phone_number}"

class MedicineInfo(models.Model):
    """Information about medicines that can be queried in the chatbot."""
    name = models.CharField(max_length=255, unique=True)
    generic_name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField()
    usage = models.TextField()
    side_effects = models.TextField(blank=True, null=True)
    contraindications = models.TextField(blank=True, null=True)
    dosage_info = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name

class AIDiagnosis(models.Model):
    """AI-powered diagnosis based on symptoms and image analysis."""
    chat_session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='ai_diagnoses')
    symptoms = models.ManyToManyField(Symptom, related_name='ai_diagnoses')
    possible_diseases = models.JSONField(default=list, help_text="List of possible diseases with confidence scores")
    primary_diagnosis = models.ForeignKey(Disease, on_delete=models.SET_NULL, null=True, blank=True)
    confidence_score = models.FloatField(default=0.0)
    urgency_level = models.CharField(max_length=20, choices=[
        ('LOW', 'Low Urgency'),
        ('MEDIUM', 'Medium Urgency'),
        ('HIGH', 'High Urgency'),
        ('EMERGENCY', 'Emergency - Seek immediate care')
    ], default='MEDIUM')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"AI Diagnosis for {self.chat_session.user.phone_number} - {self.urgency_level}"

class HealthMetrics(models.Model):
    """Health metrics and vital signs for AI analysis."""
    chat_session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='health_metrics')
    blood_pressure_systolic = models.PositiveIntegerField(blank=True, null=True)
    blood_pressure_diastolic = models.PositiveIntegerField(blank=True, null=True)
    heart_rate = models.PositiveIntegerField(blank=True, null=True)
    temperature = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True)
    blood_sugar = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    height = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    recorded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Health metrics for {self.chat_session.user.phone_number} at {self.recorded_at}"

class EmergencyAlert(models.Model):
    """Emergency alerts triggered by AI analysis."""
    ALERT_TYPE = (
        ('CRITICAL_VITALS', 'Critical Vital Signs'),
        ('SEVERE_SYMPTOMS', 'Severe Symptoms'),
        ('IMAGE_ANOMALY', 'Critical Image Finding'),
        ('SYMPTOM_COMBINATION', 'Dangerous Symptom Combination'),
    )
    
    chat_session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='emergency_alerts')
    alert_type = models.CharField(max_length=25, choices=ALERT_TYPE)
    message = models.TextField()
    severity = models.CharField(max_length=20, choices=[
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical')
    ], default='MEDIUM')
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.get_alert_type_display()} Alert - {self.severity} for {self.chat_session.user.phone_number}"
