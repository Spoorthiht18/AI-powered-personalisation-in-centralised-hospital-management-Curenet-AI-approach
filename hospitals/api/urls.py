from django.urls import path
from . import views

app_name = 'hospitals_api'

urlpatterns = [
    # Hospital listing and details
    path('', views.hospital_list_api, name='hospital_list_api'),
    path('<int:hospital_id>/', views.hospital_detail_api, name='hospital_detail_api'),
    path('search/', views.search_hospitals_api, name='search_hospitals_api'),
    path('nearby/', views.nearby_hospitals_api, name='nearby_hospitals_api'),
    
    # Doctor listing and details
    path('doctors/', views.doctor_list_api, name='doctor_list_api'),
    path('doctors/<int:doctor_id>/', views.doctor_detail_api, name='doctor_detail_api'),
    path('doctors/search/', views.search_doctors_api, name='search_doctors_api'),
] 