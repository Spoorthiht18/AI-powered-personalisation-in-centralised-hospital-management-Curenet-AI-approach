from django.urls import path
from . import views

app_name = 'appointments_api'

urlpatterns = [
    # Appointment management
    path('', views.appointment_list_api, name='appointment_list_api'),
    path('create/', views.create_appointment_api, name='create_appointment_api'),
    path('<int:appointment_id>/', views.appointment_detail_api, name='appointment_detail_api'),
    path('<int:appointment_id>/cancel/', views.cancel_appointment_api, name='cancel_appointment_api'),
    path('<int:appointment_id>/reschedule/', views.reschedule_appointment_api, name='reschedule_appointment_api'),
    
    # Medical records
    path('medical-records/', views.medical_record_list_api, name='medical_record_list_api'),
    path('medical-records/<int:record_id>/', views.medical_record_detail_api, name='medical_record_detail_api'),
    
    # Queue token management
    path('queue-tokens/', views.create_queue_token_api, name='create_queue_token_api'),
    path('queue-tokens/my-tokens/', views.get_user_tokens_api, name='get_user_tokens_api'),
    path('queue-tokens/<int:token_id>/cancel/', views.cancel_queue_token_api, name='cancel_queue_token_api'),
] 