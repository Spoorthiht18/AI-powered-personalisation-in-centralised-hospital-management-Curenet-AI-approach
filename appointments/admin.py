from django.contrib import admin
from .models import (
    Appointment, 
    MedicalRecord, 
    VideoSession, 
    PatientMedicalHistory,
    Prescription,
    QueueToken
)

class MedicalRecordInline(admin.StackedInline):
    model = MedicalRecord
    can_delete = False
    show_change_link = True

class VideoSessionInline(admin.StackedInline):
    model = VideoSession
    can_delete = False
    show_change_link = True

class PrescriptionInline(admin.TabularInline):
    model = Prescription
    extra = 1

class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'appointment_date', 'appointment_time', 'appointment_type', 'status', 'token_number']
    list_filter = ['status', 'appointment_type', 'appointment_date']
    search_fields = ['patient__phone_number', 'doctor__name', 'reason_for_visit', 'notes']
    readonly_fields = ['meeting_id']
    date_hierarchy = 'appointment_date'
    inlines = [MedicalRecordInline, VideoSessionInline]

class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ['appointment', 'diagnosis', 'follow_up_date', 'created_at']
    list_filter = ['follow_up_date', 'created_at']
    search_fields = ['appointment__patient__phone_number', 'diagnosis', 'symptoms', 'prescriptions']
    inlines = [PrescriptionInline]

class VideoSessionAdmin(admin.ModelAdmin):
    list_display = ['appointment', 'meeting_id', 'start_time', 'end_time', 'duration_in_minutes']
    list_filter = ['start_time']
    search_fields = ['appointment__patient__phone_number', 'meeting_id']
    readonly_fields = ['meeting_id']

class PatientMedicalHistoryAdmin(admin.ModelAdmin):
    list_display = ['patient', 'updated_at']
    search_fields = ['patient__phone_number', 'chronic_diseases', 'allergies', 'surgeries']

class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ['medicine_name', 'medical_record', 'dosage', 'frequency', 'duration', 'created_at']
    list_filter = ['created_at']
    search_fields = ['medicine_name', 'medical_record__appointment__patient__phone_number', 'dosage']

class QueueTokenAdmin(admin.ModelAdmin):
    list_display = ['token_number', 'patient', 'doctor', 'hospital', 'department', 'status', 'priority', 'created_at']
    list_filter = ['status', 'priority', 'department', 'created_at']
    search_fields = ['token_number', 'patient__phone_number', 'doctor__name', 'hospital__name']
    readonly_fields = ['token_number', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    list_editable = ['status', 'priority']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('patient', 'doctor', 'hospital')

admin.site.register(Appointment, AppointmentAdmin)
admin.site.register(MedicalRecord, MedicalRecordAdmin)
admin.site.register(VideoSession, VideoSessionAdmin)
admin.site.register(PatientMedicalHistory, PatientMedicalHistoryAdmin)
admin.site.register(Prescription, PrescriptionAdmin)
admin.site.register(QueueToken, QueueTokenAdmin)
