from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json
from ..models import HospitalProfile, Doctor, Specialization, HospitalRating, DoctorRating

@csrf_exempt
def hospital_list_api(request):
    """API endpoint to list hospitals."""
    hospitals = []  # This would fetch real hospitals in a real app
    return JsonResponse({'hospitals': hospitals})

@csrf_exempt
def hospital_detail_api(request, hospital_id):
    """API endpoint to get hospital details."""
    # This would fetch a real hospital in a real app
    hospital = {
        'id': hospital_id,
        'name': 'Demo Hospital',
        'address': '123 Medical St',
        'contact': '123-456-7890',
        'rating': 4.5,
    }
    return JsonResponse({'hospital': hospital})

@csrf_exempt
def search_hospitals_api(request):
    """API endpoint to search hospitals."""
    query = request.GET.get('q', '')
    hospitals = []  # This would search hospitals in a real app
    return JsonResponse({'hospitals': hospitals, 'query': query})

@csrf_exempt
def nearby_hospitals_api(request):
    """API endpoint to find nearby hospitals."""
    if request.method == 'GET':
        try:
            latitude = request.GET.get('latitude')
            longitude = request.GET.get('longitude')
            
            if not latitude or not longitude:
                return JsonResponse({
                    'success': False,
                    'message': 'Latitude and longitude are required'
                }, status=400)
            
            try:
                lat = float(latitude)
                lon = float(longitude)
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid coordinates provided'
                }, status=400)
            
            # Get verified and approved hospitals with coordinates
            from ..models import HospitalProfile
            from math import radians, cos, sin, asin, sqrt
            
            hospitals = HospitalProfile.objects.filter(
                is_verified=True, 
                is_approved=True,
                user__profile__latitude__isnull=False,
                user__profile__longitude__isnull=False
            ).select_related('user', 'user__profile')
            
            # Calculate distance for each hospital with radius filtering
            hospitals_with_distance = []
            MAX_DISTANCE_KM = 50  # 50km radius
            MAX_RESULTS = 100     # Limit results for performance
            
            for hospital in hospitals:
                if hospital.user.profile.latitude and hospital.user.profile.longitude:
                    # Haversine formula for distance calculation
                    lat1, lon1, lat2, lon2 = map(radians, [lat, lon, 
                                                          hospital.user.profile.latitude, 
                                                          hospital.user.profile.longitude])
                    
                    dlat = lat2 - lat1
                    dlon = lon2 - lon1
                    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
                    c = 2 * asin(sqrt(a))
                    distance = c * 6371  # Earth radius in km
                    
                    # Only include hospitals within 50km radius
                    if distance <= MAX_DISTANCE_KM:
                        hospitals_with_distance.append({
                            'id': hospital.id,
                            'name': hospital.hospital_name,
                            'unique_id': hospital.unique_hospital_id,
                            'address': hospital.user.profile.address or 'Address not available',
                            'emergency_contact': hospital.emergency_contact,
                            'ambulance_number': hospital.ambulance_number,
                            'distance': round(distance, 2),
                            'latitude': hospital.user.profile.latitude,
                            'longitude': hospital.user.profile.longitude
                        })
                        
                        # Limit results for performance
                        if len(hospitals_with_distance) >= MAX_RESULTS:
                            break
            
            # Sort by distance (nearest first)
            hospitals_with_distance.sort(key=lambda x: x['distance'])
            
            return JsonResponse({
                'success': True,
                'hospitals': hospitals_with_distance,
                'user_location': {
                    'latitude': lat,
                    'longitude': lon
                },
                'total_found': len(hospitals_with_distance)
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error finding nearby hospitals: {str(e)}'
            }, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt
def doctor_list_api(request):
    """API endpoint to list doctors."""
    doctors = []  # This would fetch real doctors in a real app
    return JsonResponse({'doctors': doctors})

@csrf_exempt
def doctor_detail_api(request, doctor_id):
    """API endpoint to get doctor details."""
    # This would fetch a real doctor in a real app
    doctor = {
        'id': doctor_id,
        'name': 'Dr. Demo',
        'specialization': 'General Medicine',
        'experience': 10,
        'rating': 4.8,
    }
    return JsonResponse({'doctor': doctor})

@csrf_exempt
def search_doctors_api(request):
    """API endpoint to search doctors."""
    query = request.GET.get('q', '')
    doctors = []  # This would search doctors in a real app
    return JsonResponse({'doctors': doctors, 'query': query}) 