from django.urls import path
from . import views

app_name = 'chatbot_api'

urlpatterns = [
    # Chatbot API endpoints
    path('start-session/', views.start_chat_session_api, name='start_chat_session_api'),
    path('end-session/<str:session_id>/', views.end_chat_session_api, name='end_chat_session_api'),
    path('send-message/', views.send_message_api, name='send_message_api'),
    
    # Session history API
    path('sessions/', views.chat_sessions_api, name='chat_sessions_api'),
    path('sessions/<str:session_id>/', views.chat_session_detail_api, name='chat_session_detail_api'),
    path('sessions/<str:session_id>/messages/', views.chat_messages_api, name='chat_messages_api'),
    
    # Symptom reporting API
    path('report-symptom/', views.report_symptom_api, name='report_symptom_api'),
    path('symptoms/', views.symptoms_list_api, name='symptoms_list_api'),
    
    # AI recommendations API
    path('recommendations/<str:session_id>/', views.recommendations_api, name='recommendations_api'),
    
    # Medicine information API
    path('medicines/search/', views.search_medicines_api, name='search_medicines_api'),
    path('medicines/<int:medicine_id>/', views.medicine_detail_api, name='medicine_detail_api'),
    
    # Disease information API
    path('diseases/search/', views.search_diseases_api, name='search_diseases_api'),
    path('diseases/<int:disease_id>/', views.disease_detail_api, name='disease_detail_api'),
] 