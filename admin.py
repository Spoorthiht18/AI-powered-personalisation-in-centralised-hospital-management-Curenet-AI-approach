from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, OTP, UserProfile, PatientProfile

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'User Profile'

class PatientProfileInline(admin.StackedInline):
    model = PatientProfile
    can_delete = False
    verbose_name_plural = 'Patient Profile'
    fk_name = 'user'

class UserAdmin(BaseUserAdmin):
    ordering = ['phone_number']
    list_display = ['phone_number', 'user_type', 'first_name', 'last_name', 'is_active', 'is_staff']
    list_filter = ['user_type', 'is_active', 'is_staff']
    search_fields = ['phone_number', 'first_name', 'last_name']
    
    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Account type'), {'fields': ('user_type',)}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'password1', 'password2', 'user_type'),
        }),
    )
    
    def get_inlines(self, request, obj=None):
        if obj:
            if obj.user_type == 'PATIENT':
                return [UserProfileInline, PatientProfileInline]
            else:
                return [UserProfileInline]
        return []

class OTPAdmin(admin.ModelAdmin):
    list_display = ['user', 'otp_code', 'is_verified', 'created_at', 'expires_at']
    list_filter = ['is_verified', 'created_at']
    search_fields = ['user__phone_number', 'otp_code']
    readonly_fields = ['created_at', 'expires_at']

admin.site.register(User, UserAdmin)
admin.site.register(OTP, OTPAdmin)
admin.site.register(UserProfile)
admin.site.register(PatientProfile)
