from django.urls import path
from . import views

app_name = 'hospitals'

urlpatterns = [
    # Hospital listing and details
    path('', views.hospital_list, name='hospital_list'),
    path('<int:hospital_id>/', views.hospital_detail, name='hospital_detail'),
    path('search/', views.search_hospitals, name='search_hospitals'),
    path('nearby/', views.nearby_hospitals, name='nearby_hospitals'),
    path('location-demo/', views.location_demo, name='location_demo'),
    
    # Doctor listing and details
    path('doctors/', views.doctor_list, name='doctor_list'),
    path('doctors/<int:doctor_id>/', views.doctor_detail, name='doctor_detail'),
    path('doctors/search/', views.search_doctors, name='search_doctors'),
    
    # Hospital registration and management
    path('register/', views.hospital_register, name='hospital_register'),
    path('register/verify/<str:verification_code>/', views.verify_hospital, name='verify_hospital'),
    path('dashboard/', views.hospital_dashboard, name='hospital_dashboard'),
    path('profile/edit/', views.edit_hospital_profile, name='edit_hospital_profile'),
    
    # Doctor management
    path('doctors/add/', views.add_doctor, name='add_doctor'),
    path('doctors/<int:doctor_id>/edit/', views.edit_doctor, name='edit_doctor'),
    path('doctors/<int:doctor_id>/delete/', views.delete_doctor, name='delete_doctor'),
    
    # Ratings and reviews
    path('<int:hospital_id>/rate/', views.rate_hospital, name='rate_hospital'),
    path('doctors/<int:doctor_id>/rate/', views.rate_doctor, name='rate_doctor'),
    
    # Specialization
    path('specializations/', views.specialization_list, name='specialization_list'),
    path('specializations/<int:specialization_id>/', views.specialization_detail, name='specialization_detail'),
] 