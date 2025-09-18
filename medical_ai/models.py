from django.db import models
from django.conf import settings

class Symptom(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    severity_level = models.IntegerField(
        choices=[
            (1, 'Mild'),
            (2, 'Moderate'),
            (3, 'Severe')
        ],
        default=1
    )
    
    def __str__(self):
        return self.name

class Disease(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    symptoms = models.ManyToManyField(Symptom, related_name='diseases')
    risk_level = models.IntegerField(
        choices=[
            (1, 'Low'),
            (2, 'Medium'),
            (3, 'High')
        ],
        default=1
    )
    
    def __str__(self):
        return self.name

class MedicalReport(models.Model):
    REPORT_TYPES = [
        ('XRAY', 'X-Ray'),
        ('MRI', 'MRI Scan'),
        ('CT', 'CT Scan'),
        ('LAB', 'Laboratory Report'),
        ('OTHER', 'Other'),
    ]
    
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    report_type = models.CharField(max_length=10, choices=REPORT_TYPES)
    report_file = models.FileField(upload_to='medical_reports/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    analysis_result = models.JSONField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.get_report_type_display()} - {self.patient.username} - {self.uploaded_at}"

class DiagnosisSession(models.Model):
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    symptoms = models.JSONField(null=True, blank=True)
    prediction = models.JSONField(null=True, blank=True)
    confidence_score = models.FloatField(null=True, blank=True)
    reported_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Session for {self.patient.username} - {self.reported_at}"

class AIDiagnosis(models.Model):
    DIAGNOSIS_TYPES = [
        ('LIVE_CAMERA', 'Live Camera'),
        ('UPLOADED_IMAGE', 'Uploaded Image'),
        ('SYMPTOM_ANALYSIS', 'Symptom Analysis'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    diagnosis_type = models.CharField(max_length=20, choices=DIAGNOSIS_TYPES)
    predicted_disease = models.CharField(max_length=100)
    confidence_score = models.FloatField()
    recommendations = models.JSONField(null=True, blank=True)
    raw_analysis = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.predicted_disease} ({self.confidence_score:.2f})"

class MedicalImage(models.Model):
    IMAGE_TYPES = [
        ('UPLOADED', 'Uploaded'),
        ('CAMERA_CAPTURE', 'Camera Capture'),
        ('REPORT_IMAGE', 'Report Image'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='medical_images/')
    image_type = models.CharField(max_length=20, choices=IMAGE_TYPES)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.image_type} - {self.uploaded_at}"

class ImageAnalysis(models.Model):
    medical_image = models.ForeignKey(MedicalImage, on_delete=models.CASCADE)
    predicted_disease = models.CharField(max_length=100)
    confidence_score = models.FloatField()
    analysis_data = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Analysis for {self.medical_image} - {self.predicted_disease}"

class PatientSymptom(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    symptom = models.ForeignKey(Symptom, on_delete=models.CASCADE)
    severity = models.IntegerField(choices=[(1, 'Mild'), (2, 'Moderate'), (3, 'Severe')])
    reported_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.symptom.name}"

class AIRecommendation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    recommendation_text = models.TextField()
    priority = models.IntegerField(choices=[(1, 'Low'), (2, 'Medium'), (3, 'High')])
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Recommendation for {self.user.username} - {self.priority}"

class MedicineInfo(models.Model):
    name = models.CharField(max_length=200)
    generic_name = models.CharField(max_length=200, blank=True)
    description = models.TextField()
    dosage = models.CharField(max_length=100, blank=True)
    side_effects = models.TextField(blank=True)
    contraindications = models.TextField(blank=True)
    
    def __str__(self):
        return self.name


class HealthMetrics(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    blood_pressure_systolic = models.IntegerField(null=True, blank=True)
    blood_pressure_diastolic = models.IntegerField(null=True, blank=True)
    heart_rate = models.IntegerField(null=True, blank=True)
    temperature = models.FloatField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True)
    recorded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.recorded_at}"

class EmergencyAlert(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    alert_type = models.CharField(max_length=50)
    severity = models.CharField(max_length=20, choices=[('LOW', 'Low'), ('MEDIUM', 'Medium'), ('HIGH', 'High'), ('CRITICAL', 'Critical')])
    message = models.TextField()
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.alert_type} - {self.severity}"