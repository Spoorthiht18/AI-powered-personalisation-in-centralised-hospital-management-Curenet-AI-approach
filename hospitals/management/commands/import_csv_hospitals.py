import csv
import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from hospitals.models import HospitalProfile, Doctor, Specialization
from accounts.models import Profile
import re
from decimal import Decimal

User = get_user_model()

class Command(BaseCommand):
    help = 'Import hospitals from hospital_directory.csv file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--csv-file',
            type=str,
            default='hospital_directory.csv',
            help='Path to the CSV file'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be imported without actually importing'
        )

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        dry_run = options['dry_run']
        
        if not os.path.exists(csv_file):
            self.stdout.write(
                self.style.ERROR(f'CSV file not found: {csv_file}')
            )
            return
        
        self.stdout.write(
            self.style.SUCCESS(f'Starting import from {csv_file}')
        )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No data will be imported')
            )
        
        imported_count = 0
        error_count = 0
        
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row_num, row in enumerate(reader, start=2):  # Start from 2 to account for header
                try:
                    if dry_run:
                        self.stdout.write(f"Would import: {row.get('Hospital_Name', 'Unknown')}")
                        continue
                    
                    # Extract coordinates from Location_Coordinates
                    coordinates = self.parse_coordinates(row.get('Location_Coordinates', ''))
                    
                    # Create or get user
                    user = self.create_or_get_user(row)
                    
                    # Create or get profile
                    profile = self.create_or_get_profile(user, row, coordinates)
                    
                    # Create or get hospital profile
                    hospital = self.create_or_get_hospital(user, row)
                    
                    # Create doctors if available
                    if row.get('Number_Doctor') and int(row.get('Number_Doctor', 0)) > 0:
                        self.create_doctors(hospital, row)
                    
                    imported_count += 1
                    
                    if imported_count % 100 == 0:
                        self.stdout.write(f"Imported {imported_count} hospitals...")
                        
                except Exception as e:
                    error_count += 1
                    self.stdout.write(
                        self.style.ERROR(f'Error importing row {row_num}: {str(e)}')
                    )
                    continue
        
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(f'Dry run completed. Would import {imported_count} hospitals.')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Import completed. Imported {imported_count} hospitals with {error_count} errors.')
            )

    def parse_coordinates(self, coord_string):
        """Parse coordinates from various formats."""
        if not coord_string:
            return None, None
        
        # Remove extra characters and split
        coord_string = str(coord_string).strip()
        
        # Try to extract coordinates using regex
        # Pattern for coordinates like "12.9716, 77.5946" or "12.9716,77.5946"
        coord_pattern = r'(-?\d+\.?\d*)\s*[,;]\s*(-?\d+\.?\d*)'
        match = re.search(coord_pattern, coord_string)
        
        if match:
            try:
                lat = float(match.group(1))
                lon = float(match.group(2))
                return lat, lon
            except ValueError:
                pass
        
        # If no pattern match, try to split by common separators
        for separator in [',', ';', '|', '\t']:
            if separator in coord_string:
                parts = coord_string.split(separator)
                if len(parts) >= 2:
                    try:
                        lat = float(parts[0].strip())
                        lon = float(parts[1].strip())
                        return lat, lon
                    except ValueError:
                        continue
        
        return None, None

    def create_or_get_user(self, row):
        """Create or get user based on hospital data."""
        hospital_name = row.get('Hospital_Name', '').strip()
        phone = row.get('Mobile_Number', '').strip()
        email = row.get('Hospital_Primary_Email_Id', '').strip()
        
        # Generate unique username
        base_username = f"hospital_{hospital_name.lower().replace(' ', '_')[:20]}"
        username = base_username
        counter = 1
        
        while User.objects.filter(username=username).exists():
            username = f"{base_username}_{counter}"
            counter += 1
        
        # Create user if doesn't exist
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email if email else f"{username}@curenetai.com",
                'phone_number': phone if phone else f"9999999999",
                'user_type': 'HOSPITAL',
                'is_active': True,
                'is_verified': True,
                'is_staff': False,
                'is_superuser': False,
            }
        )
        
        if created:
            # Set a default password
            user.set_password('Hospital@123')
            user.save()
        
        return user

    def create_or_get_profile(self, user, row, coordinates):
        """Create or get user profile."""
        profile, created = Profile.objects.get_or_create(
            user=user,
            defaults={
                'full_name': row.get('Hospital_Name', '').strip(),
                'address': self.build_address(row),
                'latitude': coordinates[0] if coordinates[0] else Decimal('0.000000'),
                'longitude': coordinates[1] if coordinates[1] else Decimal('0.000000'),
            }
        )
        
        if not created:
            # Update existing profile with new data
            profile.full_name = row.get('Hospital_Name', '').strip()
            profile.address = self.build_address(row)
            if coordinates[0] and coordinates[1]:
                profile.latitude = coordinates[0]
                profile.longitude = coordinates[1]
            profile.save()
        
        return profile

    def build_address(self, row):
        """Build complete address from row data."""
        address_parts = []
        
        if row.get('Address_Original_First_Line'):
            address_parts.append(row['Address_Original_First_Line'].strip())
        
        if row.get('Town'):
            address_parts.append(row['Town'].strip())
        
        if row.get('Subtown'):
            address_parts.append(row['Subtown'].strip())
        
        if row.get('Village'):
            address_parts.append(row['Village'].strip())
        
        if row.get('District'):
            address_parts.append(row['District'].strip())
        
        if row.get('State'):
            address_parts.append(row['State'].strip())
        
        if row.get('Pincode'):
            address_parts.append(f"PIN: {row['Pincode'].strip()}")
        
        return ', '.join(address_parts) if address_parts else 'Address not available'

    def create_or_get_hospital(self, user, row):
        """Create or get hospital profile."""
        hospital, created = HospitalProfile.objects.get_or_create(
            user=user,
            defaults={
                'hospital_name': row.get('Hospital_Name', '').strip(),
                'unique_hospital_id': self.generate_unique_id(row),
                'is_approved': True,  # Auto-approve imported hospitals
                'is_verified': True,
                'emergency_contact': row.get('Emergency_Num', '').strip(),
                'ambulance_number': row.get('Ambulance_Phone_No', '').strip(),
                'hospital_category': row.get('Hospital_Category', '').strip(),
                'hospital_care_type': row.get('Hospital_Care_Type', '').strip(),
                'discipline_systems': row.get('Discipline_Systems_of_Medicine', '').strip(),
                'specialties': row.get('Specialties', '').strip(),
                'facilities': row.get('Facilities', '').strip(),
                'accreditation': row.get('Accreditation', '').strip(),
                'registration_number': row.get('Hospital_Regis_Number', '').strip(),
                'established_year': row.get('Establised_Year', '').strip(),
                'total_beds': self.parse_number(row.get('Total_Num_Beds', '0')),
                'number_doctors': self.parse_number(row.get('Number_Doctor', '0')),
                'emergency_services': row.get('Emergency_Services', '').strip(),
                'tariff_range': row.get('Tariff_Range', '').strip(),
                'admin_notes': f"Imported from CSV - {row.get('Location', 'Unknown location')}",
                'approved_by': User.objects.filter(is_superuser=True).first(),
            }
        )
        
        if not created:
            # Update existing hospital with new data
            hospital.hospital_name = row.get('Hospital_Name', '').strip()
            hospital.emergency_contact = row.get('Emergency_Num', '').strip()
            hospital.ambulance_number = row.get('Ambulance_Phone_No', '').strip()
            hospital.hospital_category = row.get('Hospital_Category', '').strip()
            hospital.hospital_care_type = row.get('Hospital_Care_Type', '').strip()
            hospital.discipline_systems = row.get('Discipline_Systems_of_Medicine', '').strip()
            hospital.specialties = row.get('Specialties', '').strip()
            hospital.facilities = row.get('Facilities', '').strip()
            hospital.accreditation = row.get('Accreditation', '').strip()
            hospital.registration_number = row.get('Hospital_Regis_Number', '').strip()
            hospital.established_year = row.get('Establised_Year', '').strip()
            hospital.total_beds = self.parse_number(row.get('Total_Num_Beds', '0'))
            hospital.number_doctors = self.parse_number(row.get('Number_Doctor', '0'))
            hospital.emergency_services = row.get('Emergency_Services', '').strip()
            hospital.tariff_range = row.get('Tariff_Range', '').strip()
            hospital.save()
        
        return hospital

    def create_doctors(self, hospital, row):
        """Create doctors for the hospital."""
        num_doctors = self.parse_number(row.get('Number_Doctor', '0'))
        num_consultants = self.parse_number(row.get('Num_Mediconsultant_or_Expert', '0'))
        
        # Create specialization if not exists
        specialization, _ = Specialization.objects.get_or_create(
            name='General Medicine',
            defaults={'description': 'General medical practice'}
        )
        
        # Create doctors
        for i in range(min(num_doctors, 5)):  # Limit to 5 doctors per hospital
            doctor_name = f"Dr. {hospital.hospital_name} Doctor {i+1}"
            
            doctor, created = Doctor.objects.get_or_create(
                name=doctor_name,
                hospital=hospital,
                defaults={
                    'specialization': specialization,
                    'qualification': 'MBBS',
                    'experience_years': 5,
                    'consultation_fee': 500,
                    'is_available': True,
                }
            )

    def generate_unique_id(self, row):
        """Generate unique hospital ID."""
        state = row.get('State', 'UNK')[:3].upper()
        district = row.get('District', 'UNK')[:3].upper()
        hospital_name = row.get('Hospital_Name', 'HOSP')[:3].upper()
        
        base_id = f"{state}{district}{hospital_name}"
        counter = 1
        unique_id = base_id
        
        while HospitalProfile.objects.filter(unique_hospital_id=unique_id).exists():
            unique_id = f"{base_id}{counter:03d}"
            counter += 1
        
        return unique_id

    def parse_number(self, value):
        """Parse numeric values safely."""
        if not value:
            return 0
        try:
            return int(value)
        except (ValueError, TypeError):
            return 0
