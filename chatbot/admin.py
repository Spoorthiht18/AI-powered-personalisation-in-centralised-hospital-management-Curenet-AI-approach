from django.contrib import admin
from .models import (
    ChatSession, 
    ChatMessage, 
    Symptom, 
    Disease, 
    DiseaseSymptom,
    PatientSymptom,
    AIRecommendation,
    MedicineInfo
)

class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ['message_type', 'content', 'timestamp']
    can_delete = False

class PatientSymptomInline(admin.TabularInline):
    model = PatientSymptom
    extra = 0

class AIRecommendationInline(admin.TabularInline):
    model = AIRecommendation
    extra = 0
    readonly_fields = ['recommendation_type', 'content', 'confidence_score', 'created_at']

class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'session_id', 'is_active', 'started_at', 'ended_at', 'duration_in_minutes']
    list_filter = ['is_active', 'started_at']
    search_fields = ['user__phone_number', 'session_id']
    readonly_fields = ['session_id', 'started_at', 'ended_at']
    inlines = [ChatMessageInline, PatientSymptomInline, AIRecommendationInline]

class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['session', 'message_type', 'content_short', 'timestamp']
    list_filter = ['message_type', 'timestamp']
    search_fields = ['session__user__phone_number', 'content']
    
    def content_short(self, obj):
        return obj.content[:50] + ('...' if len(obj.content) > 50 else '')
    content_short.short_description = 'Content'

class DiseaseSymptomInline(admin.TabularInline):
    model = DiseaseSymptom
    extra = 1

class SymptomAdmin(admin.ModelAdmin):
    list_display = ['name', 'severity_level', 'get_specializations']
    list_filter = ['severity_level', 'related_specializations']
    search_fields = ['name', 'description']
    filter_horizontal = ['related_specializations']
    
    def get_specializations(self, obj):
        return ", ".join([spec.name for spec in obj.related_specializations.all()])
    get_specializations.short_description = 'Related Specializations'

class DiseaseAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_specializations', 'get_symptoms_count']
    search_fields = ['name', 'description']
    filter_horizontal = ['specializations']
    inlines = [DiseaseSymptomInline]
    
    def get_specializations(self, obj):
        return ", ".join([spec.name for spec in obj.specializations.all()])
    get_specializations.short_description = 'Specializations'
    
    def get_symptoms_count(self, obj):
        return obj.symptoms.count()
    get_symptoms_count.short_description = 'Symptoms Count'

class DiseaseSymptomAdmin(admin.ModelAdmin):
    list_display = ['disease', 'symptom', 'correlation_strength']
    list_filter = ['disease', 'symptom']
    search_fields = ['disease__name', 'symptom__name']

class PatientSymptomAdmin(admin.ModelAdmin):
    list_display = ['chat_session', 'symptom', 'severity_reported', 'reported_at']
    list_filter = ['severity_reported', 'reported_at']
    search_fields = ['chat_session__user__phone_number', 'symptom__name']

class AIRecommendationAdmin(admin.ModelAdmin):
    list_display = ['chat_session', 'recommendation_type', 'content_short', 'confidence_score', 'created_at']
    list_filter = ['recommendation_type', 'created_at']
    search_fields = ['chat_session__user__phone_number', 'content']
    
    def content_short(self, obj):
        return obj.content[:50] + ('...' if len(obj.content) > 50 else '')
    content_short.short_description = 'Content'

class MedicineInfoAdmin(admin.ModelAdmin):
    list_display = ['name', 'generic_name']
    search_fields = ['name', 'generic_name', 'description', 'usage']

admin.site.register(ChatSession, ChatSessionAdmin)
admin.site.register(ChatMessage, ChatMessageAdmin)
admin.site.register(Symptom, SymptomAdmin)
admin.site.register(Disease, DiseaseAdmin)
admin.site.register(DiseaseSymptom, DiseaseSymptomAdmin)
admin.site.register(PatientSymptom, PatientSymptomAdmin)
admin.site.register(AIRecommendation, AIRecommendationAdmin)
admin.site.register(MedicineInfo, MedicineInfoAdmin)
