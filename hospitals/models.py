from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import User, UserProfile
from django.utils import timezone

class HospitalProfile(models.Model):
    """Additional profile information specific to hospitals."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='hospital_profile')
    hospital_name = models.CharField(max_length=255)
    registration_number = models.CharField(max_length=100, unique=True)
    unique_hospital_id = models.CharField(max_length=20, unique=True, blank=True, null=True, 
                                       help_text="Unique ID assigned by admin")
    established_year = models.PositiveIntegerField(blank=True, null=True)
    registration_certificate = models.FileField(upload_to='hospital_certificates/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False, help_text="Admin approval status")
    verification_code = models.CharField(max_length=20, unique=True, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    facilities = models.TextField(blank=True, null=True)
    
    # Contact information
    website = models.URLField(blank=True, null=True)
    emergency_contact = models.CharField(max_length=15, blank=True, null=True)
    ambulance_number = models.CharField(max_length=15, blank=True, null=True)
    
    # Admin approval fields
    admin_notes = models.TextField(blank=True, null=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_hospitals')
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Additional fields from CSV
    hospital_category = models.CharField(max_length=100, blank=True)
    hospital_care_type = models.CharField(max_length=100, blank=True)
    discipline_systems = models.CharField(max_length=200, blank=True)
    specialties = models.TextField(blank=True)
    facilities = models.TextField(blank=True)
    accreditation = models.CharField(max_length=200, blank=True)
    registration_number = models.CharField(max_length=100, blank=True)
    established_year = models.CharField(max_length=10, blank=True)
    total_beds = models.IntegerField(default=0)
    number_doctors = models.IntegerField(default=0)
    emergency_services = models.CharField(max_length=200, blank=True)
    tariff_range = models.CharField(max_length=100, blank=True)
    bloodbank_phone = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)
    nodal_person = models.CharField(max_length=100, blank=True)
    nodal_person_phone = models.CharField(max_length=20, blank=True)
    nodal_person_email = models.EmailField(blank=True)
    town = models.CharField(max_length=100, blank=True)
    subtown = models.CharField(max_length=100, blank=True)
    village = models.CharField(max_length=100, blank=True)
    state_id = models.CharField(max_length=10, blank=True)
    district_id = models.CharField(max_length=10, blank=True)
    
    class Meta:
        verbose_name = "Hospital Profile"
        verbose_name_plural = "Hospital Profiles"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.hospital_name} ({self.unique_hospital_id or 'Pending'})"
    
    def save(self, *args, **kwargs):
        # Generate unique hospital ID if not provided and approved
        if self.is_approved and not self.unique_hospital_id:
            self.unique_hospital_id = self.generate_unique_id()
        super().save(*args, **kwargs)
    
    def generate_unique_id(self):
        """Generate a unique hospital ID."""
        import random
        import string
        
        # Format: HOSP-YYYY-XXXX (e.g., HOSP-2025-1234)
        year = timezone.now().year
        while True:
            # Generate 4 random digits
            random_digits = ''.join(random.choices(string.digits, k=4))
            unique_id = f"HOSP-{year}-{random_digits}"
            
            # Check if this ID already exists
            if not HospitalProfile.objects.filter(unique_hospital_id=unique_id).exists():
                return unique_id
    
    def approve(self, admin_user, notes=""):
        """Approve the hospital registration."""
        self.is_approved = True
        self.is_verified = True
        self.approved_by = admin_user
        self.approved_at = timezone.now()
        self.admin_notes = notes
        self.save()
        
        # Send approval notification
        self.send_approval_notification()
    
    def reject(self, admin_user, reason):
        """Reject the hospital registration."""
        self.is_approved = False
        self.is_verified = False
        self.rejection_reason = reason
        self.approved_by = admin_user
        self.approved_at = timezone.now()
        self.save()
        
        # Send rejection notification
        self.send_rejection_notification()
    
    def send_approval_notification(self):
        """Send approval notification to hospital."""
        try:
            from accounts.services import sms_service
            message = f"Congratulations! Your hospital {self.hospital_name} has been approved. Your unique ID is: {self.unique_hospital_id}. You can now access your dashboard."
            sms_service.send_welcome_message(self.user.phone_number, self.hospital_name)
        except Exception as e:
            print(f"Failed to send approval notification: {e}")
    
    def send_rejection_notification(self):
        """Send rejection notification to hospital."""
        try:
            from accounts.services import sms_service
            message = f"Your hospital registration for {self.hospital_name} has been reviewed. Reason: {self.rejection_reason}. Please contact support for assistance."
            # You can implement email notification here
        except Exception as e:
            print(f"Failed to send rejection notification: {e}")
    
    def average_rating(self):
        ratings = self.ratings.all()
        if ratings.exists():
            return sum(rating.rating for rating in ratings) / ratings.count()
        return 0
    
    @property
    def status_display(self):
        """Get human-readable status."""
        if self.is_approved:
            return "Approved"
        elif self.rejection_reason:
            return "Rejected"
        else:
            return "Pending Approval"

class Specialization(models.Model):
    """Medical specializations for doctors and hospitals."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name

class Doctor(models.Model):
    """Doctors working in hospitals."""
    hospital = models.ForeignKey(HospitalProfile, on_delete=models.CASCADE, related_name='doctors')
    name = models.CharField(max_length=255)
    qualification = models.CharField(max_length=255)
    specializations = models.ManyToManyField(Specialization, related_name='doctors')
    experience_years = models.PositiveIntegerField(default=0)
    photo = models.ImageField(upload_to='doctor_photos/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2)
    is_available = models.BooleanField(default=True)
    does_home_visit = models.BooleanField(default=False)
    home_visit_fee = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    # Available days and timings
    available_days = models.CharField(max_length=100, blank=True, null=True, 
                                   help_text="Comma-separated days (e.g., 'Monday,Tuesday,Friday')")
    available_from = models.TimeField(blank=True, null=True)
    available_to = models.TimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Dr. {self.name} - {self.hospital.hospital_name}"
    
    def average_rating(self):
        ratings = self.ratings.all()
        if ratings.exists():
            return sum(rating.rating for rating in ratings) / ratings.count()
        return 0
    
    def get_available_days_list(self):
        if self.available_days:
            return [day.strip() for day in self.available_days.split(',')]
        return []

class HospitalRating(models.Model):
    """Ratings given to hospitals by patients."""
    hospital = models.ForeignKey(HospitalProfile, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    review = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('hospital', 'user')
        
    def __str__(self):
        return f"{self.hospital.hospital_name} - {self.rating} stars"

class DoctorRating(models.Model):
    """Ratings given to doctors by patients."""
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    review = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('doctor', 'user')
        
    def __str__(self):
        return f"Dr. {self.doctor.name} - {self.rating} stars"

class HospitalGallery(models.Model):
    """Images for hospital gallery."""
    hospital = models.ForeignKey(HospitalProfile, on_delete=models.CASCADE, related_name='gallery')
    image = models.ImageField(upload_to='hospital_gallery/')
    caption = models.CharField(max_length=255, blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Hospital Galleries"
    
    def __str__(self):
        return f"Gallery image for {self.hospital.hospital_name}"
