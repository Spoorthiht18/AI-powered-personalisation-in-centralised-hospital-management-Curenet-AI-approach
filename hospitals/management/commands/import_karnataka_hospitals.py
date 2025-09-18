import csv
from django.core.management.base import BaseCommand
from hospitals.models import HospitalProfile
from accounts.models import User, UserProfile
from django.db import transaction

class Command(BaseCommand):
    help = 'Import hospitals from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        with open(csv_file, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                phone_number = row['phone_number']
                email = row.get('email', '')
                user, created = User.objects.get_or_create(phone_number=phone_number, defaults={
                    'email': email,
                    'user_type': 'HOSPITAL',
                })
                if created:
                    UserProfile.objects.create(user=user, address=row.get('address', ''), latitude=row.get('latitude') or None, longitude=row.get('longitude') or None)
                else:
                    user.profile.address = row.get('address', '')
                    user.profile.latitude = row.get('latitude') or None
                    user.profile.longitude = row.get('longitude') or None
                    user.profile.save()
                with transaction.atomic():
                    hospital_profile, created = HospitalProfile.objects.get_or_create(
                        user=user,
                        defaults={
                            'hospital_name': row['hospital_name'],
                            'registration_number': row['registration_number'],
                            'established_year': row.get('established_year') or None,
                            'registration_certificate': row.get('registration_certificate') or None,
                            'is_verified': row.get('is_verified', 'False').lower() == 'true',
                            'verification_code': row.get('verification_code', ''),
                            'description': row.get('description', ''),
                            'facilities': row.get('facilities', ''),
                            'website': row.get('website', ''),
                            'emergency_contact': row.get('emergency_contact', ''),
                            'ambulance_number': row.get('ambulance_number', ''),
                        }
                    )
                    if not created:
                        hospital_profile.hospital_name = row['hospital_name']
                        hospital_profile.registration_number = row['registration_number']
                        hospital_profile.established_year = row.get('established_year') or None
                        hospital_profile.is_verified = row.get('is_verified', 'False').lower() == 'true'
                        hospital_profile.verification_code = row.get('verification_code', '')
                        hospital_profile.description = row.get('description', '')
                        hospital_profile.facilities = row.get('facilities', '')
                        hospital_profile.website = row.get('website', '')
                        hospital_profile.emergency_contact = row.get('emergency_contact', '')
                        hospital_profile.ambulance_number = row.get('ambulance_number', '')
                        hospital_profile.registration_certificate = row.get('registration_certificate') or None
                        hospital_profile.save()
                self.stdout.write(self.style.SUCCESS(f"Imported/updated hospital: {row['hospital_name']}")) 