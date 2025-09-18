from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
from django.db.models import Avg, Count, Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .models import HospitalProfile, Doctor, Specialization, HospitalRating, DoctorRating
from accounts.models import User, UserProfile
from django.db import transaction
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import uuid
from math import radians, cos, sin, asin, sqrt

# Create your views here.

# Hospital listing and details
def hospital_list(request):
    """Display list of hospitals with filtering and sorting."""
    hospitals = (
        HospitalProfile.objects.filter(is_verified=True, is_approved=True)
        .select_related('user', 'user__profile')
        .prefetch_related('doctors', 'ratings', 'gallery')
        .annotate(
            avg_rating=Avg('ratings__rating'),
            ratings_count=Count('ratings', distinct=True),
            doctors_count=Count('doctors', distinct=True),
        )
    )
    
    # Get filter parameters
    hospital_type = request.GET.get('type', '')
    specialization = request.GET.get('specialization', '')
    location = request.GET.get('location', '')
    rating = request.GET.get('rating', '')
    
    # Get sort parameter
    sort_by = request.GET.get('sort', 'name')  # Default sort by name
    
    # Apply filters
    if hospital_type:
        hospitals = hospitals.filter(description__icontains=hospital_type)
    
    if specialization:
        hospitals = hospitals.filter(doctors__specializations__name__icontains=specialization).distinct()
    
    if location:
        hospitals = hospitals.filter(user__profile__address__icontains=location)
    
    if rating:
        try:
            min_rating = float(rating)
            hospitals = hospitals.filter(avg_rating__gte=min_rating)
        except ValueError:
            pass
    
    # Apply sorting
    sort_options = {
        'name': 'hospital_name',
        'name_desc': '-hospital_name',
        'rating': 'avg_rating',
        'rating_desc': '-avg_rating',
        'reviews': 'ratings_count',
        'reviews_desc': '-ratings_count',
        'doctors': 'doctors_count',
        'doctors_desc': '-doctors_count',
        'created': 'created_at',
        'created_desc': '-created_at',
        'emergency': 'emergency_contact',
        'emergency_desc': '-emergency_contact',
    }
    
    if sort_by in sort_options:
        hospitals = hospitals.order_by(sort_options[sort_by])
    else:
        hospitals = hospitals.order_by('hospital_name')  # Default fallback

    # Pagination
    page_number = request.GET.get('page', 1)
    paginator = Paginator(hospitals, 12)
    page_obj = paginator.get_page(page_number)
    
    # Get all specializations for filter dropdown
    specializations = Specialization.objects.all().order_by('name')
    
    # Get unique hospital types from descriptions
    hospital_types = ['Multi-Specialty', 'Cardiac Specialty', 'Orthopedic Specialty', 'Pediatric Specialty', 'Psychiatric Specialty', 'Government General']
    
    context = {
        'hospitals': page_obj.object_list,
        'specializations': specializations,
        'hospital_types': hospital_types,
        'page_obj': page_obj,
        'paginator': paginator,
        'current_filters': {
            'type': hospital_type,
            'specialization': specialization,
            'location': location,
            'rating': rating,
        }
    }
    return render(request, 'hospitals/hospital_list.html', context)

def hospital_detail(request, hospital_id):
    """Display details of a specific hospital."""
    hospital = get_object_or_404(HospitalProfile.objects.select_related('user'), id=hospital_id, is_verified=True)
    doctors = hospital.doctors.all().select_related('hospital').prefetch_related('specializations')
    ratings = hospital.ratings.all().select_related('user')
    
    context = {
        'hospital': hospital,
        'doctors': doctors,
        'ratings': ratings,
    }
    return render(request, 'hospitals/hospital_detail.html', context)

def search_hospitals(request):
    """Search hospitals with comprehensive search across all fields."""
    query = request.GET.get('q', '')
    category_filter = request.GET.get('category', '')
    state_filter = request.GET.get('state', '')
    district_filter = request.GET.get('district', '')
    specialty_filter = request.GET.get('specialty', '')
    sort_by = request.GET.get('sort', 'name')  # Default sort by name
    
    hospitals = HospitalProfile.objects.filter(is_verified=True, is_approved=True)
    
    if query:
        # Comprehensive search across multiple fields
        hospitals = hospitals.filter(
            Q(hospital_name__icontains=query) |
            Q(user__profile__address__icontains=query) |
            Q(specialties__icontains=query) |
            Q(facilities__icontains=query) |
            Q(hospital_category__icontains=query) |
            Q(hospital_care_type__icontains=query) |
            Q(discipline_systems__icontains=query) |
            Q(town__icontains=query) |
            Q(subtown__icontains=query) |
            Q(village__icontains=query) |
            Q(user__profile__full_name__icontains=query)
        ).distinct()
    
    # Apply filters
    if category_filter:
        hospitals = hospitals.filter(hospital_category__icontains=category_filter)
    
    if state_filter:
        hospitals = hospitals.filter(user__profile__address__icontains=state_filter)
    
    if district_filter:
        hospitals = hospitals.filter(user__profile__address__icontains=district_filter)
    
    if specialty_filter:
        hospitals = hospitals.filter(specialties__icontains=specialty_filter)
    
    # Optimize queries
    hospitals = hospitals.select_related('user', 'user__profile').prefetch_related(
        'doctors', 'ratings', 'gallery'
    ).annotate(
        avg_rating=Avg('ratings__rating'),
        ratings_count=Count('ratings', distinct=True),
        doctors_count=Count('doctors', distinct=True)
    )
    
    # Apply sorting
    sort_options = {
        'name': 'hospital_name',
        'name_desc': '-hospital_name',
        'rating': 'avg_rating',
        'rating_desc': '-avg_rating',
        'reviews': 'ratings_count',
        'reviews_desc': '-ratings_count',
        'doctors': 'doctors_count',
        'doctors_desc': '-doctors_count',
        'created': 'created_at',
        'created_desc': '-created_at',
        'emergency': 'emergency_contact',
        'emergency_desc': '-emergency_contact',
    }
    
    if sort_by in sort_options:
        hospitals = hospitals.order_by(sort_options[sort_by])
    else:
        hospitals = hospitals.order_by('hospital_name')  # Default fallback
    
    # Get unique values for filters
    categories = HospitalProfile.objects.filter(
        is_verified=True, is_approved=True
    ).exclude(hospital_category='').values_list('hospital_category', flat=True).distinct()
    
    states = HospitalProfile.objects.filter(
        is_verified=True, is_approved=True
    ).exclude(user__profile__address='').values_list('user__profile__address', flat=True).distinct()
    
    # Pagination
    paginator = Paginator(hospitals, 12)
    page = request.GET.get('page')
    try:
        hospitals = paginator.page(page)
    except PageNotAnInteger:
        hospitals = paginator.page(1)
    except EmptyPage:
        hospitals = paginator.page(paginator.num_pages)
    
    context = {
        'hospitals': hospitals,
        'query': query,
        'categories': categories,
        'states': states,
        'selected_category': category_filter,
        'selected_state': state_filter,
        'selected_district': district_filter,
        'selected_specialty': specialty_filter,
        'total_results': paginator.count,
    }
    
    return render(request, 'hospitals/search_results.html', context)

def nearby_hospitals(request):
    """Find hospitals near user's location."""
    # Get user's location from request parameters or session
    latitude = request.GET.get('latitude')
    longitude = request.GET.get('longitude')
    sort_by = request.GET.get('sort', 'distance')  # Default sort by distance
    
    if not latitude or not longitude:
        # If no coordinates provided, show limited verified hospitals
        hospitals = HospitalProfile.objects.filter(
            is_verified=True, 
            is_approved=True
        ).select_related('user', 'user__profile').prefetch_related('doctors', 'ratings')[:50]  # Limit to 50 hospitals
        
        context = {
            'hospitals': hospitals,
            'location_provided': False,
            'message': 'Please enable location access to find nearby hospitals.'
        }
        return render(request, 'hospitals/nearby_hospitals.html', context)
    
    try:
        lat = float(latitude)
        lon = float(longitude)
        
        # Get verified and approved hospitals with coordinates
        hospitals = HospitalProfile.objects.filter(
            is_verified=True, 
            is_approved=True,
            user__profile__latitude__isnull=False,
            user__profile__longitude__isnull=False
        ).select_related('user', 'user__profile').prefetch_related('doctors', 'ratings')
        
        # Calculate distance for each hospital and filter by radius (50km)
        hospitals_with_distance = []
        MAX_DISTANCE_KM = 50  # 50km radius
        MAX_RESULTS = 100     # Limit results for performance
        
        for hospital in hospitals:
            if hospital.user.profile.latitude and hospital.user.profile.longitude:
                distance = calculate_distance(
                    lat, lon, 
                    hospital.user.profile.latitude, 
                    hospital.user.profile.longitude
                )
                
                # Only include hospitals within 50km radius
                if distance <= MAX_DISTANCE_KM:
                    hospitals_with_distance.append({
                        'hospital': hospital,
                        'distance': round(distance, 2)
                    })
                    
                    # Limit results for performance
                    if len(hospitals_with_distance) >= MAX_RESULTS:
                        break
        
        # Apply sorting
        sort_options = {
            'distance': lambda x: x['distance'],
            'distance_desc': lambda x: -x['distance'],
            'name': lambda x: x['hospital'].hospital_name.lower(),
            'name_desc': lambda x: -ord(x['hospital'].hospital_name[0].lower()) if x['hospital'].hospital_name else 0,
            'rating': lambda x: x['hospital'].avg_rating or 0,
            'rating_desc': lambda x: -(x['hospital'].avg_rating or 0),
        }
        
        if sort_by in sort_options:
            hospitals_with_distance.sort(key=sort_options[sort_by])
        else:
            # Default sort by distance (nearest first)
            hospitals_with_distance.sort(key=lambda x: x['distance'])
        
        context = {
            'hospitals': [item['hospital'] for item in hospitals_with_distance],
            'distances': {item['hospital'].id: item['distance'] for item in hospitals_with_distance},
            'user_latitude': lat,
            'user_longitude': lon,
            'location_provided': True,
            'total_hospitals': len(hospitals_with_distance),
            'search_radius_km': MAX_DISTANCE_KM,
            'current_sort': sort_by
        }
        
    except (ValueError, TypeError):
        context = {
            'hospitals': [],
            'location_provided': False,
            'message': 'Invalid location coordinates provided.'
        }
    
    return render(request, 'hospitals/nearby_hospitals.html', context)

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    
    # Radius of earth in kilometers
    r = 6371
    
    return c * r

def location_demo(request):
    """Demo page for testing location functionality."""
    return render(request, 'hospitals/location_demo.html')

# Doctor listing and details
def doctor_list(request):
    """Display list of doctors with filtering."""
    doctors = Doctor.objects.select_related('hospital', 'hospital__user').prefetch_related('specializations', 'ratings').filter(is_available=True)
    
    # Get filter parameters
    specialization = request.GET.get('specialization', '')
    hospital = request.GET.get('hospital', '')
    experience = request.GET.get('experience', '')
    fee_range = request.GET.get('fee_range', '')
    home_visit = request.GET.get('home_visit', '')
    
    # Apply filters
    if specialization:
        doctors = doctors.filter(specializations__name__icontains=specialization)
    
    if hospital:
        doctors = doctors.filter(hospital__hospital_name__icontains=hospital)
    
    if experience:
        try:
            min_experience = int(experience)
            doctors = doctors.filter(experience_years__gte=min_experience)
        except ValueError:
            pass
    
    if fee_range:
        if fee_range == 'low':
            doctors = doctors.filter(consultation_fee__lte=1000)
        elif fee_range == 'medium':
            doctors = doctors.filter(consultation_fee__gt=1000, consultation_fee__lte=2000)
        elif fee_range == 'high':
            doctors = doctors.filter(consultation_fee__gt=2000)
    
    if home_visit:
        if home_visit == 'yes':
            doctors = doctors.filter(does_home_visit=True)
        elif home_visit == 'no':
            doctors = doctors.filter(does_home_visit=False)
    
    # Get all specializations for filter dropdown
    specializations = Specialization.objects.all().order_by('name')
    
    # Get all hospitals for filter dropdown
    hospitals = HospitalProfile.objects.filter(is_verified=True).order_by('hospital_name')
    
    context = {
        'doctors': doctors,
        'specializations': specializations,
        'hospitals': hospitals,
        'current_filters': {
            'specialization': specialization,
            'hospital': hospital,
            'experience': experience,
            'fee_range': fee_range,
            'home_visit': home_visit,
        }
    }
    return render(request, 'hospitals/doctor_list.html', context)

def doctor_detail(request, doctor_id):
    """Display details of a specific doctor."""
    doctor = get_object_or_404(
        Doctor.objects.select_related('hospital', 'hospital__user')
        .prefetch_related('specializations', 'ratings'),
        id=doctor_id
    )
    similar_doctors = Doctor.objects.filter(
        specializations__in=doctor.specializations.all()
    ).exclude(id=doctor.id).distinct()[:3]
    
    context = {
        'doctor': doctor,
        'similar_doctors': similar_doctors,
        'available_days': doctor.get_available_days_list(),
    }
    return render(request, 'hospitals/doctor_detail.html', context)
    context = {
        'doctor': doctor,
        'similar_doctors': similar_doctors,
    }
    return render(request, 'hospitals/doctor_detail.html', context)

def search_doctors(request):
    """Search for doctors based on criteria."""
    query = request.GET.get('q', '')
    doctors = []  # This would search for doctors in a real app
    context = {
        'doctors': doctors,
        'query': query,
    }
    return render(request, 'hospitals/doctor_list.html', context)

# Hospital registration and management
def hospital_register(request):
    """Register a new hospital."""
    if not request.user.is_anonymous and hasattr(request.user, 'user_type') and request.user.user_type == 'HOSPITAL':
        # Prevent duplicate registration
        if hasattr(request.user, 'hospital_profile'):
            if request.user.hospital_profile.is_approved:
                messages.info(request, 'Your hospital is already registered and approved.')
                return redirect('hospitals:hospital_dashboard')
            elif request.user.hospital_profile.rejection_reason:
                messages.warning(request, f'Your previous registration was rejected. Reason: {request.user.hospital_profile.rejection_reason}')
            else:
                messages.info(request, 'Your hospital registration is pending admin approval.')
                return redirect('hospitals:hospital_dashboard')
    
    if request.method == 'POST':
        hospital_name = request.POST.get('hospital_name')
        registration_number = request.POST.get('registration_number')
        phone_number = request.POST.get('phone_number')
        established_year = request.POST.get('established_year')
        description = request.POST.get('description')
        email = request.POST.get('email')
        website = request.POST.get('website')
        emergency_contact = request.POST.get('emergency_contact')
        ambulance_number = request.POST.get('ambulance_number')
        address = request.POST.get('address')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        facilities = request.POST.get('facilities')
        registration_certificate = request.FILES.get('registration_certificate')
        agree_terms = request.POST.get('agree_terms')

        if not (hospital_name and registration_number and phone_number and address and registration_certificate and agree_terms):
            messages.error(request, 'Please fill all required fields and agree to the terms.')
            return render(request, 'hospitals/hospital_register.html')

        # Check if phone number is already used for a different user type
        existing_user = User.objects.filter(phone_number=phone_number).first()
        if existing_user and existing_user.user_type != 'HOSPITAL':
            messages.error(request, 'This phone number is already registered as a different user type.')
            return render(request, 'hospitals/hospital_register.html')

        # Check if registration number already exists
        if HospitalProfile.objects.filter(registration_number=registration_number).exists():
            messages.error(request, 'This registration number is already registered.')
            return render(request, 'hospitals/hospital_register.html')

        # Create user for hospital (if not exists)
        user, created = User.objects.get_or_create(phone_number=phone_number, defaults={
            'email': email or '',
            'user_type': 'HOSPITAL',
        })
        if created:
            # Create a profile for the user
            UserProfile.objects.create(user=user, address=address, latitude=latitude or None, longitude=longitude or None)
        else:
            # Update address if needed
            user.profile.address = address
            user.profile.latitude = latitude or None
            user.profile.longitude = longitude or None
            user.profile.save()

        # Save registration certificate
        cert_path = default_storage.save(f"hospital_certificates/{registration_certificate.name}", ContentFile(registration_certificate.read()))

        # Generate a unique verification code
        verification_code = str(uuid.uuid4()).replace('-', '')[:10]

        # Create hospital profile
        with transaction.atomic():
            hospital_profile, created = HospitalProfile.objects.get_or_create(
                user=user,
                defaults={
                    'hospital_name': hospital_name,
                    'registration_number': registration_number,
                    'established_year': established_year or None,
                    'registration_certificate': cert_path,
                    'is_verified': False,
                    'is_approved': False,  # New hospitals start as unapproved
                    'description': description,
                    'facilities': facilities,
                    'website': website,
                    'emergency_contact': emergency_contact,
                    'ambulance_number': ambulance_number,
                    'verification_code': verification_code,
                }
            )
            if not created:
                # Update fields if profile exists
                hospital_profile.hospital_name = hospital_name
                hospital_profile.registration_number = registration_number
                hospital_profile.established_year = established_year or None
                hospital_profile.registration_certificate = cert_path
                hospital_profile.is_verified = False
                hospital_profile.is_approved = False
                hospital_profile.description = description
                hospital_profile.facilities = facilities
                hospital_profile.website = website
                hospital_profile.emergency_contact = emergency_contact
                hospital_profile.ambulance_number = ambulance_number
                hospital_profile.verification_code = verification_code
                hospital_profile.save()

        messages.success(request, 'Your hospital registration has been submitted and is pending admin approval. You will be notified once approved.')
        return redirect('hospitals:hospital_register')

    return render(request, 'hospitals/hospital_register.html')

def verify_hospital(request, verification_code):
    """Verify a hospital using verification code."""
    # This would verify the hospital in a real app
    return redirect('hospitals:hospital_dashboard')

@login_required
def hospital_dashboard(request):
    """Display dashboard for hospital users."""
    user = request.user
    if user.user_type == 'HOSPITAL':
        try:
            hospital_profile = user.hospital_profile
            context = {'hospital': hospital_profile}
            return render(request, 'hospitals/hospital_dashboard.html', context)
        except HospitalProfile.DoesNotExist:
            return redirect('hospitals:hospital_register')
    else:
        messages.error(request, 'You are not authorized to access the hospital dashboard.')
        return redirect('accounts:profile')

@login_required
def edit_hospital_profile(request):
    """Edit hospital profile."""
    if request.method == 'POST':
        # This would update the profile in a real app
        pass
    return render(request, 'hospitals/edit_hospital_profile.html')

# Doctor management
@login_required
def add_doctor(request):
    """Add a new doctor to a hospital."""
    if request.method == 'POST':
        # This would add a doctor in a real app
        pass
    return render(request, 'hospitals/add_doctor.html')

@login_required
def edit_doctor(request, doctor_id):
    """Edit doctor information."""
    if request.method == 'POST':
        # This would update the doctor in a real app
        pass
    return render(request, 'hospitals/edit_doctor.html')

@login_required
def delete_doctor(request, doctor_id):
    """Delete a doctor."""
    # This would delete the doctor in a real app
    return redirect('hospitals:hospital_dashboard')

# Ratings and reviews
@login_required
def rate_hospital(request, hospital_id):
    """Rate a hospital."""
    if request.method == 'POST':
        # This would save the rating in a real app
        pass
    return redirect('hospitals:hospital_detail', hospital_id=hospital_id)

@login_required
def rate_doctor(request, doctor_id):
    """Rate a doctor."""
    if request.method == 'POST':
        # This would save the rating in a real app
        pass
    return redirect('hospitals:doctor_detail', doctor_id=doctor_id)

# Specialization
def specialization_list(request):
    """Display list of specializations."""
    specializations = []  # This would fetch real specializations in a real app
    context = {
        'specializations': specializations,
    }
    return render(request, 'hospitals/specialization_list.html', context)

def specialization_detail(request, specialization_id):
    """Display details of a specific specialization."""
    specialization = {}  # This would fetch a real specialization in a real app
    context = {
        'specialization': specialization,
    }
    return render(request, 'hospitals/specialization_detail.html', context)
