from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    # Main chatbot interface
    path('', views.chatbot_interface, name='chatbot_interface'),
    
    # Chat session management
    path('start-session/', views.start_chat_session, name='start_chat_session'),
    path('end-session/<str:session_id>/', views.end_chat_session, name='end_chat_session'),
    path('send-message/<str:session_id>/', views.send_message, name='send_message'),
    
    # AI-powered features
    path('upload-image/', views.upload_medical_image, name='upload_medical_image'),
    path('record-metrics/', views.record_health_metrics, name='record_health_metrics'),
    path('get-recommendations/', views.get_doctor_recommendations, name='get_doctor_recommendations'),
    
    # Symptom and disease information
    path('symptoms/', views.symptoms_list, name='symptoms_list'),
    path('symptoms/<int:symptom_id>/', views.symptom_detail, name='symptom_detail'),
    path('diseases/', views.diseases_list, name='diseases_list'),
    path('diseases/<int:disease_id>/', views.disease_detail, name='disease_detail'),
    
    # Medicine information
    path('medicines/', views.medicines_list, name='medicines_list'),
    path('medicines/<int:medicine_id>/', views.medicine_detail, name='medicine_detail'),
    path('medicines/search/', views.search_medicines, name='search_medicines'),
    
    # AI recommendations and history
    path('recommendations/<str:session_id>/', views.recommendations, name='recommendations'),
    path('chat-history/', views.chat_history, name='chat_history'),
    path('chat-session/<str:session_id>/', views.chat_session_detail, name='chat_session_detail'),
] 