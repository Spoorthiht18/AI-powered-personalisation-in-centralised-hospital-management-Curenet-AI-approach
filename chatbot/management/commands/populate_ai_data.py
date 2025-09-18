from django.core.management.base import BaseCommand
from chatbot.models import Symptom, Disease, DiseaseSymptom, MedicineInfo
from hospitals.models import Specialization

class Command(BaseCommand):
    help = 'Populate database with sample symptoms, diseases, and medicines for AI chatbot'

    def handle(self, *args, **options):
        self.stdout.write('Starting to populate AI data...')
        
        # Create specializations if they don't exist
        specializations = self._create_specializations()
        
        # Create symptoms
        symptoms = self._create_symptoms()
        
        # Create diseases
        diseases = self._create_diseases(specializations)
        
        # Create disease-symptom relationships
        self._create_disease_symptom_relationships(diseases, symptoms)
        
        # Create medicines
        self._create_medicines()
        
        self.stdout.write(self.style.SUCCESS('Successfully populated AI data!'))

    def _create_specializations(self):
        """Create medical specializations."""
        spec_names = [
            'Cardiology', 'Neurology', 'Orthopedics', 'Pediatrics', 'Gynecology',
            'Oncology', 'Dermatology', 'Psychiatry', 'General Surgery', 'Internal Medicine',
            'Emergency Medicine', 'Radiology', 'Anesthesiology', 'Pathology', 'Ophthalmology',
            'ENT', 'Urology', 'Nephrology', 'Endocrinology', 'Gastroenterology'
        ]
        
        specializations = {}
        for name in spec_names:
            spec, created = Specialization.objects.get_or_create(name=name)
            specializations[name] = spec
            if created:
                self.stdout.write(f'Created specialization: {name}')
        
        return specializations

    def _create_symptoms(self):
        """Create common symptoms."""
        symptoms_data = [
            {'name': 'Fever', 'description': 'Elevated body temperature above normal range', 'severity_level': 3},
            {'name': 'Headache', 'description': 'Pain in the head or upper neck', 'severity_level': 2},
            {'name': 'Cough', 'description': 'Sudden expulsion of air from the lungs', 'severity_level': 2},
            {'name': 'Chest Pain', 'description': 'Pain or discomfort in the chest area', 'severity_level': 5},
            {'name': 'Abdominal Pain', 'description': 'Pain in the stomach or belly area', 'severity_level': 4},
            {'name': 'Nausea', 'description': 'Feeling of sickness with urge to vomit', 'severity_level': 3},
            {'name': 'Fatigue', 'description': 'Extreme tiredness and lack of energy', 'severity_level': 2},
            {'name': 'Shortness of Breath', 'description': 'Difficulty breathing or breathlessness', 'severity_level': 4},
            {'name': 'Dizziness', 'description': 'Feeling lightheaded or unsteady', 'severity_level': 3},
            {'name': 'Joint Pain', 'description': 'Pain in joints like knees, hips, or shoulders', 'severity_level': 3},
            {'name': 'Back Pain', 'description': 'Pain in the back, especially lower back', 'severity_level': 3},
            {'name': 'Sore Throat', 'description': 'Pain or irritation in the throat', 'severity_level': 2},
            {'name': 'Runny Nose', 'description': 'Excessive nasal discharge', 'severity_level': 1},
            {'name': 'Vomiting', 'description': 'Forceful expulsion of stomach contents', 'severity_level': 4},
            {'name': 'Diarrhea', 'description': 'Frequent, loose, watery stools', 'severity_level': 3},
        ]
        
        symptoms = {}
        for data in symptoms_data:
            symptom, created = Symptom.objects.get_or_create(
                name=data['name'],
                defaults=data
            )
            symptoms[data['name']] = symptom
            if created:
                self.stdout.write(f'Created symptom: {data["name"]}')
        
        return symptoms

    def _create_diseases(self, specializations):
        """Create common diseases."""
        diseases_data = [
            {
                'name': 'Common Cold',
                'description': 'Viral infection of the upper respiratory tract',
                'specializations': ['Internal Medicine', 'Pediatrics']
            },
            {
                'name': 'Influenza (Flu)',
                'description': 'Viral infection affecting the respiratory system',
                'specializations': ['Internal Medicine', 'Pediatrics']
            },
            {
                'name': 'Hypertension',
                'description': 'High blood pressure that can lead to heart problems',
                'specializations': ['Cardiology', 'Internal Medicine']
            },
            {
                'name': 'Diabetes',
                'description': 'Metabolic disorder affecting blood sugar levels',
                'specializations': ['Endocrinology', 'Internal Medicine']
            },
            {
                'name': 'Asthma',
                'description': 'Chronic respiratory condition causing breathing difficulties',
                'specializations': ['Pulmonology', 'Pediatrics']
            },
            {
                'name': 'Arthritis',
                'description': 'Inflammation of joints causing pain and stiffness',
                'specializations': ['Orthopedics', 'Rheumatology']
            },
            {
                'name': 'Depression',
                'description': 'Mental health disorder affecting mood and behavior',
                'specializations': ['Psychiatry', 'Psychology']
            },
            {
                'name': 'Migraine',
                'description': 'Severe recurring headache often with nausea',
                'specializations': ['Neurology', 'Internal Medicine']
            },
            {
                'name': 'Gastritis',
                'description': 'Inflammation of the stomach lining',
                'specializations': ['Gastroenterology', 'Internal Medicine']
            },
            {
                'name': 'Pneumonia',
                'description': 'Infection causing inflammation of air sacs in lungs',
                'specializations': ['Pulmonology', 'Internal Medicine']
            }
        ]
        
        diseases = {}
        for data in diseases_data:
            disease, created = Disease.objects.get_or_create(
                name=data['name'],
                defaults={'description': data['description']}
            )
            
            if created:
                # Add specializations
                for spec_name in data['specializations']:
                    if spec_name in specializations:
                        disease.specializations.add(specializations[spec_name])
                self.stdout.write(f'Created disease: {data["name"]}')
            
            diseases[data['name']] = disease
        
        return diseases

    def _create_disease_symptom_relationships(self, diseases, symptoms):
        """Create relationships between diseases and symptoms."""
        relationships = [
            ('Common Cold', ['Fever', 'Cough', 'Sore Throat', 'Runny Nose']),
            ('Influenza (Flu)', ['Fever', 'Cough', 'Fatigue', 'Body Aches']),
            ('Hypertension', ['Headache', 'Dizziness', 'Chest Pain']),
            ('Diabetes', ['Fatigue', 'Increased Thirst', 'Frequent Urination']),
            ('Asthma', ['Shortness of Breath', 'Cough', 'Chest Pain']),
            ('Arthritis', ['Joint Pain', 'Back Pain', 'Stiffness']),
            ('Depression', ['Fatigue', 'Mood Changes', 'Sleep Problems']),
            ('Migraine', ['Headache', 'Nausea', 'Sensitivity to Light']),
            ('Gastritis', ['Abdominal Pain', 'Nausea', 'Vomiting']),
            ('Pneumonia', ['Fever', 'Cough', 'Shortness of Breath', 'Chest Pain'])
        ]
        
        for disease_name, symptom_names in relationships:
            if disease_name in diseases:
                disease = diseases[disease_name]
                for symptom_name in symptom_names:
                    if symptom_name in symptoms:
                        symptom = symptoms[symptom_name]
                        relationship, created = DiseaseSymptom.objects.get_or_create(
                            disease=disease,
                            symptom=symptom,
                            defaults={'correlation_strength': 0.8}
                        )
                        if created:
                            self.stdout.write(f'Created relationship: {disease_name} - {symptom_name}')

    def _create_medicines(self):
        """Create sample medicine information."""
        medicines_data = [
            {
                'name': 'Paracetamol',
                'generic_name': 'Acetaminophen',
                'description': 'Pain reliever and fever reducer',
                'usage': 'Take 500-1000mg every 4-6 hours as needed for pain or fever',
                'side_effects': 'Rare side effects include allergic reactions, liver problems with high doses',
                'contraindications': 'Do not take if allergic to paracetamol or with severe liver disease',
                'dosage_info': 'Adults: 500-1000mg every 4-6 hours, max 4000mg per day'
            },
            {
                'name': 'Ibuprofen',
                'generic_name': 'Ibuprofen',
                'description': 'Non-steroidal anti-inflammatory drug for pain and inflammation',
                'usage': 'Take 200-400mg every 4-6 hours for pain or inflammation',
                'side_effects': 'May cause stomach upset, increased bleeding risk',
                'contraindications': 'Avoid if you have stomach ulcers, kidney disease, or bleeding disorders',
                'dosage_info': 'Adults: 200-400mg every 4-6 hours, max 1200mg per day'
            },
            {
                'name': 'Omeprazole',
                'generic_name': 'Omeprazole',
                'description': 'Proton pump inhibitor that reduces stomach acid production',
                'usage': 'Take 20mg once daily before breakfast for acid reflux or ulcers',
                'side_effects': 'May cause headache, diarrhea, or vitamin B12 deficiency with long-term use',
                'contraindications': 'Avoid if allergic to omeprazole or during pregnancy',
                'dosage_info': 'Adults: 20mg once daily, may increase to 40mg if needed'
            }
        ]
        
        for data in medicines_data:
            medicine, created = MedicineInfo.objects.get_or_create(
                name=data['name'],
                defaults=data
            )
            if created:
                self.stdout.write(f'Created medicine: {data["name"]}')
