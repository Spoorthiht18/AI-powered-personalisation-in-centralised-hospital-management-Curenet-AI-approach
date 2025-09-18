from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from appointments.models import QueueToken
from hospitals.models import HospitalProfile, Doctor
from datetime import timedelta
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Populate sample queue tokens for testing'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample queue tokens...')
        
        try:
            # Get or create sample data
            hospital = HospitalProfile.objects.first()
            if not hospital:
                self.stdout.write(self.style.ERROR('No hospitals found. Please create hospitals first.'))
                return
            
            doctor = Doctor.objects.filter(hospital=hospital).first()
            if not doctor:
                self.stdout.write(self.style.ERROR('No doctors found. Please create doctors first.'))
                return
            
            # Get or create a test patient
            patient, created = User.objects.get_or_create(
                phone_number='9999999999',
                defaults={
                    'user_type': 'PATIENT',
                    'is_active': True
                }
            )
            
            if created:
                self.stdout.write(f'Created test patient: {patient.phone_number}')
            
            # Clear existing tokens for today
            today = timezone.now().date()
            QueueToken.objects.filter(
                hospital=hospital,
                created_at__date=today
            ).delete()
            
            # Create sample tokens
            statuses = ['WAITING', 'CALLING', 'IN_PROGRESS', 'COMPLETED']
            priorities = ['NORMAL', 'URGENT', 'EMERGENCY']
            
            for i in range(1, 11):
                status = random.choice(statuses)
                priority = random.choice(priorities)
                
                # Create token with different timestamps
                created_at = timezone.now() - timedelta(minutes=random.randint(0, 120))
                
                token = QueueToken.objects.create(
                    token_number=i,
                    patient=patient,
                    doctor=doctor,
                    hospital=hospital,
                    department=doctor.specialization,
                    status=status,
                    priority=priority,
                    reason=f'Sample consultation {i}',
                    estimated_wait_time=random.randint(10, 45),
                    created_at=created_at
                )
                
                # Set completion time for completed tokens
                if status == 'COMPLETED':
                    token.completed_at = created_at + timedelta(minutes=random.randint(15, 60))
                    token.save()
                
                # Set calling time for calling tokens
                if status == 'CALLING':
                    token.called_at = created_at + timedelta(minutes=random.randint(5, 30))
                    token.save()
                
                self.stdout.write(f'Created token #{i} - {status} - {priority}')
            
            self.stdout.write(self.style.SUCCESS('Successfully created sample queue tokens!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating sample data: {e}'))
