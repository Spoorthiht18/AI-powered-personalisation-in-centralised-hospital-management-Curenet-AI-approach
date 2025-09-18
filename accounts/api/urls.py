from django.urls import path
from . import views

app_name = 'accounts_api'

urlpatterns = [
    # Authentication APIs
    path('login/', views.login_api, name='login_api'),
    path('logout/', views.logout_api, name='logout_api'),
    path('send-otp/', views.send_otp_api, name='send_otp_api'),
    path('verify-otp/', views.verify_otp_api, name='verify_otp_api'),
    
    # User Profile APIs
    path('profile/', views.profile_api, name='profile_api'),
    path('profile/update/', views.update_profile_api, name='update_profile_api'),
    path('patient-profile/update/', views.update_patient_profile_api, name='update_patient_profile_api'),
    
    # User Registration
    path('register/', views.register_api, name='register_api'),
] 