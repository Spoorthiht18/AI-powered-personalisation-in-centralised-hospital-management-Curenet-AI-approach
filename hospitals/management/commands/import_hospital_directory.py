from django.core.management.base import BaseCommand
from django.db import transaction
from hospitals.models import HospitalProfile, Specialization
from accounts.models import User, UserProfile
import csv
import uuid
import re

class Command(BaseCommand):
    help = 'Import hospital directory data from CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']
        
        self.stdout.write(f'Starting import from {csv_file_path}...')
        
        # Create specializations if they don't exist
        specializations_data = [
            'Cardiology', 'Neurology', 'Orthopedics', 'Pediatrics', 'Gynecology',
            'Oncology', 'Dermatology', 'Psychiatry', 'General Surgery', 'Internal Medicine',
            'Emergency Medicine', 'Radiology', 'Anesthesiology', 'Pathology', 'Ophthalmology',
            'ENT', 'Urology', 'Nephrology', 'Endocrinology', 'Gastroenterology',
            'Cardiothoracic Surgery', 'Plastic Surgery', 'Vascular Surgery', 'Neurosurgery',
            'Pediatric Surgery', 'Gynecological Surgery', 'Oncological Surgery', 'Trauma Surgery'
        ]
        
        specializations = {}
        for spec_name in specializations_data:
            spec, created = Specialization.objects.get_or_create(name=spec_name)
            specializations[spec_name] = spec
            if created:
                self.stdout.write(f'Created specialization: {spec_name}')
        
        imported_count = 0
        skipped_count = 0
        
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                for row in reader:
                    try:
                        # Skip rows with missing essential data
                        if not row.get('Hospital_Name') or not row.get('State'):
                            skipped_count += 1
                            continue
                        
                        # Extract coordinates if available
                        coordinates = row.get('Location_Coordinates', '')
                        latitude = None
                        longitude = None
                        
                        if coordinates and ',' in coordinates:
                            try:
                                coords = coordinates.split(',')
                                if len(coords) >= 2:
                                    latitude = float(coords[0].strip())
                                    longitude = float(coords[1].strip())
                            except (ValueError, IndexError):
                                pass
                        
                        # Create or get user for hospital
                        phone_number = row.get('Telephone') or row.get('Mobile_Number') or f'080{imported_count:08d}'
                        if not phone_number or phone_number == '0':
                            phone_number = f'080{imported_count:08d}'
                        
                        # Clean phone number
                        phone_number = re.sub(r'[^\d]', '', str(phone_number))
                        if len(phone_number) < 10:
                            phone_number = f'080{imported_count:08d}'
                        
                        # Make phone number unique if it already exists
                        original_phone = phone_number
                        counter = 1
                        while User.objects.filter(phone_number=phone_number).exists():
                            phone_number = f"{original_phone}_{counter}"
                            counter += 1
                        
                        user, created = User.objects.get_or_create(
                            phone_number=phone_number,
                            defaults={
                                'user_type': 'HOSPITAL',
                                'email': f'hospital_{imported_count}@example.com'
                            }
                        )
                        
                        if created:
                            # Create user profile
                            address_parts = []
                            if row.get('Address_Original_First_Line'):
                                address_parts.append(row['Address_Original_First_Line'])
                            if row.get('Town'):
                                address_parts.append(row['Town'])
                            if row.get('District'):
                                address_parts.append(row['District'])
                            if row.get('State'):
                                address_parts.append(row['State'])
                            if row.get('Pincode'):
                                address_parts.append(row['Pincode'])
                            
                            address = ', '.join(filter(None, address_parts))
                            
                            UserProfile.objects.create(
                                user=user,
                                address=address or f"Hospital in {row.get('State', 'Unknown')}",
                                latitude=latitude,
                                longitude=longitude
                            )
                        
                        # Determine hospital type from category and care type
                        hospital_type = 'Multi-Specialty'
                        if row.get('Hospital_Category'):
                            if 'cardiac' in row['Hospital_Category'].lower() or 'heart' in row['Hospital_Category'].lower():
                                hospital_type = 'Cardiac Specialty'
                            elif 'orthopedic' in row['Hospital_Category'].lower() or 'bone' in row['Hospital_Category'].lower():
                                hospital_type = 'Orthopedic Specialty'
                            elif 'pediatric' in row['Hospital_Category'].lower() or 'child' in row['Hospital_Category'].lower():
                                hospital_type = 'Pediatric Specialty'
                            elif 'psychiatric' in row['Hospital_Category'].lower() or 'mental' in row['Hospital_Category'].lower():
                                hospital_type = 'Psychiatric Specialty'
                        
                        if row.get('Hospital_Care_Type') == 'Hospital':
                            if 'government' in row.get('Hospital_Category', '').lower():
                                hospital_type = 'Government General'
                        
                        # Generate unique registration number
                        reg_number = row.get('Hospital_Regis_Number')
                        if not reg_number or reg_number == '0':
                            reg_number = f'HOSP{imported_count:06d}'
                        
                        # Check if registration number already exists and make it unique
                        counter = 1
                        original_reg_number = reg_number
                        while HospitalProfile.objects.filter(registration_number=reg_number).exists():
                            reg_number = f"{original_reg_number}_{counter}"
                            counter += 1
                        
                        # Create hospital profile
                        hospital, created = HospitalProfile.objects.get_or_create(
                            user=user,
                            defaults={
                                'hospital_name': row['Hospital_Name'],
                                'registration_number': reg_number,
                                'established_year': int(row['Establised_Year']) if row.get('Establised_Year') and row['Establised_Year'].isdigit() else None,
                                'description': f"{hospital_type} hospital in {row.get('State', 'India')}. {row.get('Hospital_Category', '')}",
                                'facilities': row.get('Facilities') or 'General healthcare services',
                                'website': row.get('Website') if row.get('Website') and row['Website'] != '0' else None,
                                'emergency_contact': row.get('Emergency_Num') if row.get('Emergency_Num') and row['Emergency_Num'] != '0' else None,
                                'ambulance_number': row.get('Ambulance_Phone_No') if row.get('Ambulance_Phone_No') and row['Ambulance_Phone_No'] != '0' else None,
                                'is_verified': True,  # Mark as verified since it's from official directory
                                'verification_code': str(uuid.uuid4()).replace('-', '')[:10]
                            }
                        )
                        
                        if created:
                            self.stdout.write(f'Created hospital: {hospital.hospital_name} in {row.get("State", "Unknown")}')
                            imported_count += 1
                        
                        # Add some sample doctors for demonstration
                        if created and imported_count <= 100:  # Limit to first 100 hospitals for demo
                            self._create_sample_doctors(hospital, specializations)
                        
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f'Error processing row {imported_count + skipped_count + 1}: {str(e)}'))
                        skipped_count += 1
                        continue
                        
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'CSV file not found: {csv_file_path}'))
            return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error reading CSV file: {str(e)}'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'Import completed! Imported {imported_count} hospitals, skipped {skipped_count} rows.'))
    
    def _create_sample_doctors(self, hospital, specializations):
        """Create sample doctors for the hospital"""
        from hospitals.models import Doctor
        
        # Sample doctor data based on hospital type
        if 'Cardiac' in hospital.description:
            specializations_to_add = ['Cardiology', 'Cardiothoracic Surgery']
        elif 'Orthopedic' in hospital.description:
            specializations_to_add = ['Orthopedics', 'General Surgery']
        elif 'Pediatric' in hospital.description:
            specializations_to_add = ['Pediatrics', 'Pediatric Surgery']
        elif 'Psychiatric' in hospital.description:
            specializations_to_add = ['Psychiatry', 'Neurology']
        else:
            specializations_to_add = ['Internal Medicine', 'General Surgery', 'Gynecology']
        
        # Create 1-3 doctors per hospital
        import random
        num_doctors = random.randint(1, 3)
        
        for i in range(num_doctors):
            spec = random.choice(specializations_to_add)
            if spec in specializations:
                doctor = Doctor.objects.create(
                    hospital=hospital,
                    name=f"Dr. Sample Doctor {i+1}",
                    qualification=f"MBBS, MD ({spec})",
                    experience_years=random.randint(5, 25),
                    consultation_fee=random.randint(500, 2500),
                    does_home_visit=random.choice([True, False]),
                    home_visit_fee=random.randint(1000, 4000) if random.choice([True, False]) else None,
                    available_days="Monday,Tuesday,Wednesday,Thursday,Friday",
                    available_from="09:00",
                    available_to="17:00",
                    bio=f"Experienced {spec} specialist",
                    is_available=True
                )
                doctor.specializations.add(specializations[spec])
