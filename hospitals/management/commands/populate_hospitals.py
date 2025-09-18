from django.core.management.base import BaseCommand
from django.db import transaction
from hospitals.models import HospitalProfile, Doctor, Specialization, HospitalRating, DoctorRating
from accounts.models import User, UserProfile
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import uuid

class Command(BaseCommand):
    help = 'Populate database with sample hospitals and doctors data'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample hospitals and doctors...')
        
        # Create specializations
        specializations_data = [
            'Cardiology', 'Neurology', 'Orthopedics', 'Pediatrics', 'Gynecology',
            'Oncology', 'Dermatology', 'Psychiatry', 'General Surgery', 'Internal Medicine',
            'Emergency Medicine', 'Radiology', 'Anesthesiology', 'Pathology', 'Ophthalmology',
            'ENT', 'Urology', 'Nephrology', 'Endocrinology', 'Gastroenterology'
        ]
        
        specializations = {}
        for spec_name in specializations_data:
            spec, created = Specialization.objects.get_or_create(name=spec_name)
            specializations[spec_name] = spec
            if created:
                self.stdout.write(f'Created specialization: {spec_name}')
        
        # Sample hospitals data
        hospitals_data = [
            {
                'name': 'Apollo Hospitals',
                'type': 'Multi-Specialty',
                'established': 1983,
                'description': 'Leading healthcare provider with world-class medical facilities and expert doctors.',
                'facilities': 'ICU, NICU, Emergency Care, Cardiac Care, Cancer Treatment, Organ Transplant',
                'address': '154, Bannerghatta Road, Bangalore, Karnataka 560076',
                'website': 'https://www.apollohospitals.com',
                'emergency': '080-71791090',
                'ambulance': '080-71791091'
            },
            {
                'name': 'Fortis Hospital',
                'type': 'Multi-Specialty',
                'established': 1996,
                'description': 'Comprehensive healthcare services with advanced medical technology.',
                'facilities': 'Cardiac Surgery, Neurology, Orthopedics, Oncology, Emergency Medicine',
                'address': '154/9, Bannerghatta Road, Opposite IIM-B, Bangalore, Karnataka 560076',
                'website': 'https://www.fortishealthcare.com',
                'emergency': '080-66214444',
                'ambulance': '080-66214445'
            },
            {
                'name': 'Manipal Hospital',
                'type': 'Multi-Specialty',
                'established': 1991,
                'description': 'Academic medical center providing comprehensive healthcare and medical education.',
                'facilities': 'Medical Education, Research, Clinical Care, Community Health',
                'address': '98, HAL Airport Road, Kodihalli, Bangalore, Karnataka 560017',
                'website': 'https://www.manipalhospitals.com',
                'emergency': '080-25023444',
                'ambulance': '080-25023445'
            },
            {
                'name': 'Narayana Health',
                'type': 'Cardiac Specialty',
                'established': 2000,
                'description': 'Specialized cardiac care with affordable healthcare solutions.',
                'facilities': 'Cardiac Surgery, Interventional Cardiology, Pediatric Cardiology, Heart Transplant',
                'address': '258/A, Bommasandra Industrial Area, Anekal Taluk, Bangalore, Karnataka 560099',
                'website': 'https://www.narayanahealth.org',
                'emergency': '080-27835000',
                'ambulance': '080-27835001'
            },
            {
                'name': 'Sparsh Hospital',
                'type': 'Orthopedic Specialty',
                'established': 2008,
                'description': 'Specialized orthopedic care with advanced surgical techniques.',
                'facilities': 'Joint Replacement, Spine Surgery, Sports Medicine, Trauma Care, Rehabilitation',
                'address': '29/1, 29/2, 29/3, PESIT Campus, Hosur Road, Bangalore, Karnataka 560100',
                'website': 'https://www.sparshhospital.com',
                'emergency': '080-28413333',
                'ambulance': '080-28413334'
            },
            {
                'name': 'Rainbow Children\'s Hospital',
                'type': 'Pediatric Specialty',
                'established': 1999,
                'description': 'Dedicated pediatric care with child-friendly environment and specialized treatments.',
                'facilities': 'Pediatric Surgery, Neonatology, Pediatric Oncology, Pediatric Cardiology',
                'address': '78, Cunningham Road, Bangalore, Karnataka 560052',
                'website': 'https://www.rainbowhospitals.in',
                'emergency': '080-22223333',
                'ambulance': '080-22223334'
            },
            {
                'name': 'NIMHANS',
                'type': 'Psychiatric Specialty',
                'established': 1925,
                'description': 'National Institute of Mental Health and Neurosciences providing specialized mental health care.',
                'facilities': 'Psychiatry, Neurology, Neurosurgery, Clinical Psychology, Social Work',
                'address': 'Hosur Road, Bangalore, Karnataka 560029',
                'website': 'https://www.nimhans.ac.in',
                'emergency': '080-26995000',
                'ambulance': '080-26995001'
            },
            {
                'name': 'Victoria Hospital',
                'type': 'Government General',
                'established': 1901,
                'description': 'Government hospital providing affordable healthcare to all sections of society.',
                'facilities': 'General Medicine, Surgery, Emergency Care, Maternity Care, Public Health',
                'address': 'Fort Road, Bangalore, Karnataka 560002',
                'website': None,
                'emergency': '080-26701150',
                'ambulance': '080-26701151'
            },
            {
                'name': 'Bowring & Lady Curzon Hospital',
                'type': 'Government General',
                'established': 1866,
                'description': 'One of the oldest government hospitals in Bangalore providing comprehensive healthcare.',
                'facilities': 'General Medicine, Surgery, Gynecology, Pediatrics, Emergency Medicine',
                'address': 'Shivajinagar, Bangalore, Karnataka 560001',
                'website': None,
                'emergency': '080-22868000',
                'ambulance': '080-22868001'
            },
            {
                'name': 'KC General Hospital',
                'type': 'Government General',
                'established': 1972,
                'description': 'Government hospital serving the northern part of Bangalore with modern facilities.',
                'facilities': 'General Medicine, Surgery, Emergency Care, Maternity Care, Public Health',
                'address': 'Malleshwaram, Bangalore, Karnataka 560003',
                'website': None,
                'emergency': '080-23341721',
                'ambulance': '080-23341722'
            }
        ]
        
        # Sample doctors data
        doctors_data = [
            # Apollo Hospitals
            {'name': 'Dr. Rajesh Kumar', 'qualification': 'MBBS, MD (Cardiology)', 'specializations': ['Cardiology'], 'experience': 15, 'consultation_fee': 1500, 'home_visit': True, 'home_visit_fee': 2500, 'days': 'Monday,Tuesday,Thursday,Friday', 'from_time': '09:00', 'to_time': '17:00'},
            {'name': 'Dr. Priya Sharma', 'qualification': 'MBBS, MS (Gynecology)', 'specializations': ['Gynecology'], 'experience': 12, 'consultation_fee': 1200, 'home_visit': False, 'days': 'Monday,Wednesday,Friday', 'from_time': '10:00', 'to_time': '16:00'},
            {'name': 'Dr. Amit Patel', 'qualification': 'MBBS, MS (General Surgery)', 'specializations': ['General Surgery'], 'experience': 18, 'consultation_fee': 1800, 'home_visit': False, 'days': 'Tuesday,Thursday,Saturday', 'from_time': '08:00', 'to_time': '18:00'},
            
            # Fortis Hospital
            {'name': 'Dr. Sanjay Gupta', 'qualification': 'MBBS, MD (Neurology)', 'specializations': ['Neurology'], 'experience': 20, 'consultation_fee': 2000, 'home_visit': True, 'home_visit_fee': 3000, 'days': 'Monday,Tuesday,Wednesday,Friday', 'from_time': '09:00', 'to_time': '17:00'},
            {'name': 'Dr. Meera Reddy', 'qualification': 'MBBS, MS (Orthopedics)', 'specializations': ['Orthopedics'], 'experience': 14, 'consultation_fee': 1600, 'home_visit': False, 'days': 'Tuesday,Thursday,Saturday', 'from_time': '10:00', 'to_time': '16:00'},
            {'name': 'Dr. Ramesh Iyer', 'qualification': 'MBBS, MD (Oncology)', 'specializations': ['Oncology'], 'experience': 16, 'consultation_fee': 2200, 'home_visit': False, 'days': 'Monday,Wednesday,Friday', 'from_time': '09:00', 'to_time': '15:00'},
            
            # Manipal Hospital
            {'name': 'Dr. Kavita Desai', 'qualification': 'MBBS, MD (Pediatrics)', 'specializations': ['Pediatrics'], 'experience': 13, 'consultation_fee': 1100, 'home_visit': True, 'home_visit_fee': 2000, 'days': 'Monday,Tuesday,Thursday,Friday', 'from_time': '09:00', 'to_time': '16:00'},
            {'name': 'Dr. Arun Kumar', 'qualification': 'MBBS, MD (Internal Medicine)', 'specializations': ['Internal Medicine'], 'experience': 17, 'consultation_fee': 1400, 'home_visit': False, 'days': 'Tuesday,Wednesday,Friday,Saturday', 'from_time': '08:00', 'to_time': '17:00'},
            {'name': 'Dr. Sunita Verma', 'qualification': 'MBBS, MS (ENT)', 'specializations': ['ENT'], 'experience': 11, 'consultation_fee': 1300, 'home_visit': False, 'days': 'Monday,Wednesday,Saturday', 'from_time': '10:00', 'to_time': '16:00'},
            
            # Narayana Health
            {'name': 'Dr. Vijay Shetty', 'qualification': 'MBBS, MS (Cardiothoracic Surgery)', 'specializations': ['Cardiology'], 'experience': 22, 'consultation_fee': 2500, 'home_visit': False, 'days': 'Monday,Tuesday,Thursday,Friday', 'from_time': '08:00', 'to_time': '18:00'},
            {'name': 'Dr. Anjali Rao', 'qualification': 'MBBS, MD (Cardiology)', 'specializations': ['Cardiology'], 'experience': 15, 'consultation_fee': 1800, 'home_visit': True, 'home_visit_fee': 2800, 'days': 'Tuesday,Wednesday,Friday,Saturday', 'from_time': '09:00', 'to_time': '17:00'},
            
            # Sparsh Hospital
            {'name': 'Dr. Deepak Jain', 'qualification': 'MBBS, MS (Orthopedics)', 'specializations': ['Orthopedics'], 'experience': 19, 'consultation_fee': 2000, 'home_visit': False, 'days': 'Monday,Tuesday,Thursday,Friday', 'from_time': '09:00', 'to_time': '17:00'},
            {'name': 'Dr. Neha Singh', 'qualification': 'MBBS, MS (Orthopedics)', 'specializations': ['Orthopedics'], 'experience': 12, 'consultation_fee': 1600, 'home_visit': False, 'days': 'Tuesday,Wednesday,Saturday', 'from_time': '10:00', 'to_time': '16:00'},
            
            # Rainbow Children's Hospital
            {'name': 'Dr. Suresh Kumar', 'qualification': 'MBBS, MD (Pediatrics)', 'specializations': ['Pediatrics'], 'experience': 16, 'consultation_fee': 1400, 'home_visit': True, 'home_visit_fee': 2200, 'days': 'Monday,Tuesday,Thursday,Friday', 'from_time': '09:00', 'to_time': '16:00'},
            {'name': 'Dr. Lakshmi Devi', 'qualification': 'MBBS, MS (Pediatric Surgery)', 'specializations': ['Pediatrics'], 'experience': 18, 'consultation_fee': 2200, 'home_visit': False, 'days': 'Tuesday,Wednesday,Friday,Saturday', 'from_time': '08:00', 'to_time': '17:00'},
            
            # NIMHANS
            {'name': 'Dr. Rajesh Kumar', 'qualification': 'MBBS, MD (Psychiatry)', 'specializations': ['Psychiatry'], 'experience': 25, 'consultation_fee': 1200, 'home_visit': False, 'days': 'Monday,Tuesday,Wednesday,Thursday', 'from_time': '09:00', 'to_time': '16:00'},
            {'name': 'Dr. Priya Sharma', 'qualification': 'MBBS, MD (Neurology)', 'specializations': ['Neurology'], 'experience': 20, 'consultation_fee': 1800, 'home_visit': False, 'days': 'Tuesday,Thursday,Friday,Saturday', 'from_time': '09:00', 'to_time': '17:00'},
            
            # Victoria Hospital
            {'name': 'Dr. Abdul Rahman', 'qualification': 'MBBS, MD (General Medicine)', 'specializations': ['Internal Medicine'], 'experience': 15, 'consultation_fee': 500, 'home_visit': False, 'days': 'Monday,Tuesday,Wednesday,Thursday,Friday', 'from_time': '08:00', 'to_time': '16:00'},
            {'name': 'Dr. Lakshmi Bai', 'qualification': 'MBBS, MS (Gynecology)', 'specializations': ['Gynecology'], 'experience': 12, 'consultation_fee': 600, 'home_visit': False, 'days': 'Monday,Wednesday,Friday', 'from_time': '09:00', 'to_time': '15:00'},
            
            # Bowring & Lady Curzon Hospital
            {'name': 'Dr. Manjunath Reddy', 'qualification': 'MBBS, MS (General Surgery)', 'specializations': ['General Surgery'], 'experience': 16, 'consultation_fee': 550, 'home_visit': False, 'days': 'Tuesday,Thursday,Saturday', 'from_time': '08:00', 'to_time': '16:00'},
            {'name': 'Dr. Geetha Kumari', 'qualification': 'MBBS, MD (Pediatrics)', 'specializations': ['Pediatrics'], 'experience': 13, 'consultation_fee': 500, 'home_visit': False, 'days': 'Monday,Tuesday,Thursday,Friday', 'from_time': '09:00', 'to_time': '15:00'},
            
            # KC General Hospital
            {'name': 'Dr. Ravi Kumar', 'qualification': 'MBBS, MD (General Medicine)', 'specializations': ['Internal Medicine'], 'experience': 14, 'consultation_fee': 500, 'home_visit': False, 'days': 'Monday,Tuesday,Wednesday,Thursday,Friday', 'from_time': '08:00', 'to_time': '16:00'},
            {'name': 'Dr. Shobha Devi', 'qualification': 'MBBS, MS (Gynecology)', 'specializations': ['Gynecology'], 'experience': 11, 'consultation_fee': 550, 'home_visit': False, 'days': 'Monday,Wednesday,Friday', 'from_time': '09:00', 'to_time': '15:00'}
        ]
        
        with transaction.atomic():
            # Create hospitals
            created_hospitals = []
            for i, hospital_data in enumerate(hospitals_data):
                # Create user for hospital
                phone_number = f'080{70000000 + i:08d}'
                user, created = User.objects.get_or_create(
                    phone_number=phone_number,
                    defaults={
                        'user_type': 'HOSPITAL',
                        'email': f'hospital{i+1}@example.com'
                    }
                )
                
                if created:
                    UserProfile.objects.create(
                        user=user,
                        address=hospital_data['address'],
                        latitude=12.9716 + (i * 0.01),
                        longitude=77.5946 + (i * 0.01)
                    )
                
                # Create hospital profile
                hospital, created = HospitalProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'hospital_name': hospital_data['name'],
                        'registration_number': f'HOSP{i+1:03d}',
                        'established_year': hospital_data['established'],
                        'description': hospital_data['description'],
                        'facilities': hospital_data['facilities'],
                        'website': hospital_data['website'],
                        'emergency_contact': hospital_data['emergency'],
                        'ambulance_number': hospital_data['ambulance'],
                        'is_verified': True,
                        'verification_code': str(uuid.uuid4()).replace('-', '')[:10]
                    }
                )
                
                if created:
                    self.stdout.write(f'Created hospital: {hospital.hospital_name}')
                
                created_hospitals.append(hospital)
            
            # Create doctors
            doctor_index = 0
            for i, hospital in enumerate(created_hospitals):
                # Add 2-3 doctors per hospital
                doctors_per_hospital = min(3, len(doctors_data) - doctor_index)
                for j in range(doctors_per_hospital):
                    if doctor_index >= len(doctors_data):
                        break
                        
                    doctor_data = doctors_data[doctor_index]
                    
                    # Create doctor
                    doctor = Doctor.objects.create(
                        hospital=hospital,
                        name=doctor_data['name'],
                        qualification=doctor_data['qualification'],
                        experience_years=doctor_data['experience'],
                        consultation_fee=doctor_data['consultation_fee'],
                        does_home_visit=doctor_data['home_visit'],
                        home_visit_fee=doctor_data.get('home_visit_fee'),
                        available_days=doctor_data['days'],
                        available_from=doctor_data['from_time'],
                        available_to=doctor_data['to_time'],
                        bio=f"Experienced {doctor_data['specializations'][0]} specialist with {doctor_data['experience']} years of practice."
                    )
                    
                    # Add specializations
                    for spec_name in doctor_data['specializations']:
                        if spec_name in specializations:
                            doctor.specializations.add(specializations[spec_name])
                    
                    self.stdout.write(f'Created doctor: {doctor.name} at {hospital.hospital_name}')
                    doctor_index += 1
            
            # Create some sample ratings
            for hospital in created_hospitals[:5]:  # Add ratings to first 5 hospitals
                for i in range(3):  # 3 ratings per hospital
                    rating_value = 4 + (i % 2)  # 4 or 5 stars
                    # Create a unique user for each rating to avoid constraint violation
                    rating_user, created = User.objects.get_or_create(
                        phone_number=f'080{80000000 + (created_hospitals.index(hospital) * 3) + i:08d}',
                        defaults={
                            'user_type': 'PATIENT',
                            'email': f'patient{created_hospitals.index(hospital) * 3 + i + 1}@example.com'
                        }
                    )
                    
                    # Check if rating already exists
                    if not HospitalRating.objects.filter(hospital=hospital, user=rating_user).exists():
                        HospitalRating.objects.create(
                            hospital=hospital,
                            user=rating_user,
                            rating=rating_value,
                            review=f"Great hospital with excellent facilities. Rating: {rating_value}/5"
                        )
            
            self.stdout.write(self.style.SUCCESS(f'Successfully created {len(created_hospitals)} hospitals and {doctor_index} doctors!'))
