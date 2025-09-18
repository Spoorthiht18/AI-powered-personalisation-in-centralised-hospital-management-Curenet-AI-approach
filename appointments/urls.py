from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    # Appointment management
    path('', views.appointment_list, name='appointment_list'),
    path('create/<int:doctor_id>/', views.create_appointment, name='create_appointment'),
    path('<int:appointment_id>/', views.appointment_detail, name='appointment_detail'),
    path('<int:appointment_id>/cancel/', views.cancel_appointment, name='cancel_appointment'),
    path('<int:appointment_id>/reschedule/', views.reschedule_appointment, name='reschedule_appointment'),
    
    # Video consultations
    path('video/<str:meeting_id>/', views.video_consultation, name='video_consultation'),
    path('video/<str:meeting_id>/start/', views.start_video_session, name='start_video_session'),
    path('video/<str:meeting_id>/end/', views.end_video_session, name='end_video_session'),
    
    # Medical records
    path('medical-records/', views.medical_record_list, name='medical_record_list'),
    path('medical-records/<int:record_id>/', views.medical_record_detail, name='medical_record_detail'),
    
    # For doctors/hospitals
    path('manage/', views.manage_appointments, name='manage_appointments'),
    path('manage/<int:appointment_id>/confirm/', views.confirm_appointment, name='confirm_appointment'),
    path('manage/<int:appointment_id>/complete/', views.complete_appointment, name='complete_appointment'),
    path('manage/<int:appointment_id>/no-show/', views.mark_no_show, name='mark_no_show'),
    
    # Medical records management (for doctors)
    path('manage/<int:appointment_id>/medical-record/create/', views.create_medical_record, name='create_medical_record'),
    path('manage/<int:appointment_id>/medical-record/update/', views.update_medical_record, name='update_medical_record'),
    
    # Prescriptions
    path('medical-records/<int:record_id>/prescriptions/add/', views.add_prescription, name='add_prescription'),
    path('medical-records/<int:record_id>/prescriptions/<int:prescription_id>/edit/', views.edit_prescription, name='edit_prescription'),
    path('medical-records/<int:record_id>/prescriptions/<int:prescription_id>/delete/', views.delete_prescription, name='delete_prescription'),
    
    # Medical history
    path('medical-history/', views.medical_history, name='medical_history'),
    path('medical-history/update/', views.update_medical_history, name='update_medical_history'),
] 