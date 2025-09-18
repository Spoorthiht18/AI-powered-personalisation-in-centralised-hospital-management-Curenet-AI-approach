from django.urls import path
from . import views

app_name = 'medical_ai'

urlpatterns = [
    path('upload-report/', views.upload_report, name='upload_report'),
    path('symptom-checker/', views.symptom_checker, name='symptom_checker'),
    path('get-symptom-questions/', views.get_symptom_questions, name='get_symptom_questions'),
    path('report-analysis/<int:report_id>/', views.view_report_analysis, name='view_report_analysis'),
    path('analyze-image/', views.analyze_image, name='analyze_image'),
    path('diagnosis-history/', views.diagnosis_history, name='diagnosis_history'),
    
    # Live diagnosis endpoints
    path('live-diagnosis/', views.live_diagnosis_camera, name='live_diagnosis_camera'),
    path('capture-and-diagnose/', views.capture_and_diagnose, name='capture_and_diagnose'),
    path('upload-and-diagnose/', views.upload_and_diagnose, name='upload_and_diagnose'),
    path('diagnosis-detail/<int:diagnosis_id>/', views.diagnosis_detail, name='diagnosis_detail'),
    path('train-model/', views.train_model_api, name='train_model_api'),
    path('diagnosis-stats/', views.get_diagnosis_stats, name='diagnosis_stats'),
]
