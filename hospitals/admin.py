from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import HospitalProfile, Doctor, Specialization, HospitalRating, DoctorRating, HospitalGallery

class HospitalGalleryInline(admin.TabularInline):
    model = HospitalGallery
    extra = 1

class DoctorInline(admin.TabularInline):
    model = Doctor
    extra = 1
    fields = ['name', 'qualification', 'experience_years', 'consultation_fee', 'is_available']

@admin.register(HospitalProfile)
class HospitalProfileAdmin(admin.ModelAdmin):
    list_display = ['hospital_name', 'unique_hospital_id', 'registration_number', 'user', 'status_display', 'is_verified', 'created_at']
    list_filter = ['is_verified', 'is_approved', 'established_year', 'created_at']
    search_fields = ['hospital_name', 'user__phone_number', 'registration_number', 'unique_hospital_id']
    readonly_fields = ['verification_code', 'created_at', 'updated_at', 'approved_by', 'approved_at']
    inlines = [DoctorInline, HospitalGalleryInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'hospital_name', 'registration_number', 'unique_hospital_id', 'established_year')
        }),
        ('Contact & Details', {
            'fields': ('description', 'facilities', 'website', 'emergency_contact', 'ambulance_number')
        }),
        ('Verification & Approval', {
            'fields': ('is_verified', 'is_approved', 'verification_code', 'registration_certificate')
        }),
        ('Admin Actions', {
            'fields': ('admin_notes', 'approved_by', 'approved_at', 'rejection_reason'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['approve_hospitals', 'reject_hospitals', 'generate_unique_ids']
    
    def status_display(self, obj):
        """Display status with color coding."""
        if obj.is_approved:
            return format_html('<span style="color: green; font-weight: bold;">✓ Approved</span>')
        elif obj.rejection_reason:
            return format_html('<span style="color: red; font-weight: bold;">✗ Rejected</span>')
        else:
            return format_html('<span style="color: orange; font-weight: bold;">⏳ Pending</span>')
    status_display.short_description = 'Status'
    
    def approve_hospitals(self, request, queryset):
        """Approve selected hospitals."""
        count = 0
        for hospital in queryset:
            if not hospital.is_approved:
                hospital.approve(request.user, "Approved by admin")
                count += 1
        
        if count == 1:
            message = "1 hospital was approved successfully."
        else:
            message = f"{count} hospitals were approved successfully."
        
        self.message_user(request, message)
    approve_hospitals.short_description = "Approve selected hospitals"
    
    def reject_hospitals(self, request, queryset):
        """Reject selected hospitals."""
        count = 0
        for hospital in queryset:
            if not hospital.is_approved:
                hospital.reject(request.user, "Rejected by admin")
                count += 1
        
        if count == 1:
            message = "1 hospital was rejected."
        else:
            message = f"{count} hospitals were rejected."
        
        self.message_user(request, message)
    reject_hospitals.short_description = "Reject selected hospitals"
    
    def generate_unique_ids(self, request, queryset):
        """Generate unique IDs for approved hospitals."""
        count = 0
        for hospital in queryset:
            if hospital.is_approved and not hospital.unique_hospital_id:
                hospital.save()  # This will trigger unique ID generation
                count += 1
        
        if count == 1:
            message = "1 unique ID was generated."
        else:
            message = f"{count} unique IDs were generated."
        
        self.message_user(request, message)
    generate_unique_ids.short_description = "Generate unique IDs for approved hospitals"
    
    def get_queryset(self, request):
        """Show pending approvals first."""
        qs = super().get_queryset(request)
        return qs.order_by('is_approved', '-created_at')

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['name', 'hospital', 'qualification', 'experience_years', 'consultation_fee', 'is_available']
    list_filter = ['is_available', 'does_home_visit', 'experience_years', 'specializations']
    search_fields = ['name', 'hospital__hospital_name', 'qualification']
    filter_horizontal = ['specializations']

@admin.register(Specialization)
class SpecializationAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']

@admin.register(HospitalRating)
class HospitalRatingAdmin(admin.ModelAdmin):
    list_display = ['hospital', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['hospital__hospital_name', 'user__phone_number']

@admin.register(DoctorRating)
class DoctorRatingAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['doctor__name', 'user__phone_number']

@admin.register(HospitalGallery)
class HospitalGalleryAdmin(admin.ModelAdmin):
    list_display = ['hospital', 'image', 'is_featured', 'created_at']
    list_filter = ['is_featured', 'created_at']
    search_fields = ['hospital__hospital_name']

