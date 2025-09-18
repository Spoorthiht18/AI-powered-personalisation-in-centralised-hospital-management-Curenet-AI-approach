import json
import random
from typing import List, Dict, Tuple
from django.db.models import Q
from hospitals.models import Doctor, Specialization, HospitalProfile
from .models import Symptom, Disease, AIDiagnosis, EmergencyAlert, HealthMetrics

class MedicalAIService:
    """Advanced AI service for medical diagnosis and image analysis."""
    
    def __init__(self):
        self.symptom_disease_mapping = self._load_symptom_disease_mapping()
        self.emergency_symptoms = self._load_emergency_symptoms()
        self.critical_vital_ranges = self._load_critical_vital_ranges()
    
    def _load_symptom_disease_mapping(self) -> Dict[str, List[Dict]]:
        """Load mapping of symptoms to possible diseases with confidence scores."""
        return {
            'fever': [
                {'disease': 'Common Cold', 'confidence': 0.7, 'urgency': 'LOW'},
                {'disease': 'Flu', 'confidence': 0.8, 'urgency': 'MEDIUM'},
                {'disease': 'COVID-19', 'confidence': 0.6, 'urgency': 'HIGH'},
                {'disease': 'Malaria', 'confidence': 0.5, 'urgency': 'HIGH'},
            ],
            'chest_pain': [
                {'disease': 'Angina', 'confidence': 0.8, 'urgency': 'HIGH'},
                {'disease': 'Heart Attack', 'confidence': 0.9, 'urgency': 'EMERGENCY'},
                {'disease': 'Pneumonia', 'confidence': 0.7, 'urgency': 'HIGH'},
                {'disease': 'Costochondritis', 'confidence': 0.6, 'urgency': 'MEDIUM'},
            ],
            'shortness_of_breath': [
                {'disease': 'Asthma', 'confidence': 0.8, 'urgency': 'HIGH'},
                {'disease': 'COPD', 'confidence': 0.7, 'urgency': 'HIGH'},
                {'disease': 'Pneumonia', 'confidence': 0.8, 'urgency': 'HIGH'},
                {'disease': 'Heart Failure', 'confidence': 0.7, 'urgency': 'EMERGENCY'},
            ],
            'headache': [
                {'disease': 'Tension Headache', 'confidence': 0.8, 'urgency': 'LOW'},
                {'disease': 'Migraine', 'confidence': 0.8, 'urgency': 'MEDIUM'},
                {'disease': 'Sinusitis', 'confidence': 0.7, 'urgency': 'LOW'},
                {'disease': 'Brain Tumor', 'confidence': 0.3, 'urgency': 'HIGH'},
            ],
            'abdominal_pain': [
                {'disease': 'Gastritis', 'confidence': 0.7, 'urgency': 'MEDIUM'},
                {'disease': 'Appendicitis', 'confidence': 0.8, 'urgency': 'HIGH'},
                {'disease': 'Gallstones', 'confidence': 0.7, 'urgency': 'HIGH'},
                {'disease': 'Food Poisoning', 'confidence': 0.6, 'urgency': 'MEDIUM'},
            ],
            'cough': [
                {'disease': 'Common Cold', 'confidence': 0.8, 'urgency': 'LOW'},
                {'disease': 'Bronchitis', 'confidence': 0.7, 'urgency': 'MEDIUM'},
                {'disease': 'Pneumonia', 'confidence': 0.7, 'urgency': 'HIGH'},
                {'disease': 'Tuberculosis', 'confidence': 0.5, 'urgency': 'HIGH'},
            ],
            'fatigue': [
                {'disease': 'Anemia', 'confidence': 0.7, 'urgency': 'MEDIUM'},
                {'disease': 'Depression', 'confidence': 0.6, 'urgency': 'MEDIUM'},
                {'disease': 'Chronic Fatigue Syndrome', 'confidence': 0.5, 'urgency': 'MEDIUM'},
                {'disease': 'Diabetes', 'confidence': 0.6, 'urgency': 'MEDIUM'},
            ],
            'nausea': [
                {'disease': 'Gastritis', 'confidence': 0.7, 'urgency': 'MEDIUM'},
                {'disease': 'Food Poisoning', 'confidence': 0.8, 'urgency': 'MEDIUM'},
                {'disease': 'Pregnancy', 'confidence': 0.6, 'urgency': 'LOW'},
                {'disease': 'Migraine', 'confidence': 0.6, 'urgency': 'MEDIUM'},
            ],
            'dizziness': [
                {'disease': 'Vertigo', 'confidence': 0.7, 'urgency': 'MEDIUM'},
                {'disease': 'Low Blood Pressure', 'confidence': 0.6, 'urgency': 'MEDIUM'},
                {'disease': 'Anemia', 'confidence': 0.6, 'urgency': 'MEDIUM'},
                {'disease': 'Inner Ear Problem', 'confidence': 0.5, 'urgency': 'LOW'},
            ],
            'joint_pain': [
                {'disease': 'Arthritis', 'confidence': 0.8, 'urgency': 'MEDIUM'},
                {'disease': 'Rheumatoid Arthritis', 'confidence': 0.7, 'urgency': 'MEDIUM'},
                {'disease': 'Gout', 'confidence': 0.6, 'urgency': 'MEDIUM'},
                {'disease': 'Lupus', 'confidence': 0.5, 'urgency': 'HIGH'},
            ]
        }
    
    def _load_emergency_symptoms(self) -> List[str]:
        """Load list of symptoms that require immediate medical attention."""
        return [
            'chest_pain', 'shortness_of_breath', 'severe_headache', 'unconsciousness',
            'severe_bleeding', 'paralysis', 'severe_burns', 'poisoning'
        ]
    
    def _load_critical_vital_ranges(self) -> Dict[str, Dict]:
        """Load critical ranges for vital signs."""
        return {
            'blood_pressure_systolic': {'min': 90, 'max': 140, 'critical_low': 80, 'critical_high': 180},
            'blood_pressure_diastolic': {'min': 60, 'max': 90, 'critical_low': 50, 'critical_high': 110},
            'heart_rate': {'min': 60, 'max': 100, 'critical_low': 40, 'critical_high': 120},
            'temperature': {'min': 36.1, 'max': 37.2, 'critical_low': 35.0, 'critical_high': 40.0},
            'blood_sugar': {'min': 70, 'max': 140, 'critical_low': 50, 'critical_high': 200},
        }
    
    def analyze_symptoms(self, symptoms: List[str], user_context: Dict = None) -> Dict:
        """Analyze symptoms and provide AI diagnosis."""
        if not symptoms:
            return {'error': 'No symptoms provided'}
        
        # Analyze each symptom
        disease_probabilities = {}
        total_confidence = 0
        urgency_level = 'LOW'
        
        for symptom in symptoms:
            symptom_lower = symptom.lower().replace(' ', '_')
            if symptom_lower in self.symptom_disease_mapping:
                for disease_info in self.symptom_disease_mapping[symptom_lower]:
                    disease_name = disease_info['disease']
                    confidence = disease_info['confidence']
                    urgency = disease_info['urgency']
                    
                    if disease_name in disease_probabilities:
                        disease_probabilities[disease_name]['confidence'] += confidence
                        disease_probabilities[disease_name]['count'] += 1
                    else:
                        disease_probabilities[disease_name] = {
                            'confidence': confidence,
                            'count': 1,
                            'urgency': urgency
                        }
                    
                    # Update overall urgency level
                    if urgency == 'EMERGENCY':
                        urgency_level = 'EMERGENCY'
                    elif urgency == 'HIGH' and urgency_level != 'EMERGENCY':
                        urgency_level = 'HIGH'
                    elif urgency == 'MEDIUM' and urgency_level not in ['EMERGENCY', 'HIGH']:
                        urgency_level = 'MEDIUM'
        
        # Calculate final confidence scores
        for disease_name, data in disease_probabilities.items():
            avg_confidence = data['confidence'] / data['count']
            disease_probabilities[disease_name]['final_confidence'] = min(avg_confidence * 1.2, 1.0)
        
        # Sort by confidence
        sorted_diseases = sorted(
            disease_probabilities.items(),
            key=lambda x: x[1]['final_confidence'],
            reverse=True
        )
        
        # Check for emergency conditions
        emergency_alert = None
        if urgency_level in ['HIGH', 'EMERGENCY']:
            emergency_alert = self._create_emergency_alert(symptoms, urgency_level)
        
        return {
            'possible_diseases': sorted_diseases[:5],  # Top 5 most likely
            'urgency_level': urgency_level,
            'emergency_alert': emergency_alert,
            'recommendations': self._generate_recommendations(sorted_diseases, urgency_level),
            'confidence_score': sum(d[1]['final_confidence'] for d in sorted_diseases[:3]) / 3
        }
    
    def analyze_medical_image(self, image_type: str, image_description: str = None) -> Dict:
        """Analyze medical images using AI (simulated for demo)."""
        # In a real implementation, this would use computer vision models
        # For demo purposes, we'll simulate AI analysis based on image type
        
        analysis_results = {
            'XRAY': {
                'normal': 0.7,
                'pneumonia': 0.2,
                'fracture': 0.1,
                'tuberculosis': 0.05
            },
            'MRI': {
                'normal': 0.8,
                'tumor': 0.1,
                'herniated_disc': 0.08,
                'stroke': 0.02
            },
            'CT': {
                'normal': 0.75,
                'appendicitis': 0.15,
                'kidney_stones': 0.08,
                'aneurysm': 0.02
            },
            'ULTRASOUND': {
                'normal': 0.8,
                'gallstones': 0.15,
                'pregnancy': 0.04,
                'ovarian_cyst': 0.01
            },
            'BLOOD_REPORT': {
                'normal': 0.6,
                'anemia': 0.2,
                'diabetes': 0.15,
                'infection': 0.05
            },
            'ECG': {
                'normal': 0.7,
                'arrhythmia': 0.2,
                'myocardial_infarction': 0.08,
                'heart_block': 0.02
            }
        }
        
        if image_type not in analysis_results:
            return {'error': 'Unsupported image type'}
        
        # Simulate AI analysis with some randomness
        results = analysis_results[image_type].copy()
        
        # Add some randomness to make it more realistic
        for condition, prob in results.items():
            variation = random.uniform(-0.1, 0.1)
            results[condition] = max(0, min(1, prob + variation))
        
        # Normalize probabilities
        total = sum(results.values())
        for condition in results:
            results[condition] = results[condition] / total
        
        # Find the most likely condition
        primary_condition = max(results.items(), key=lambda x: x[1])
        
        # Generate analysis text
        analysis_text = self._generate_image_analysis_text(image_type, primary_condition, results)
        
        # Check for critical findings
        critical_findings = self._check_critical_image_findings(image_type, primary_condition, results)
        
        return {
            'analysis_text': analysis_text,
            'detected_conditions': results,
            'primary_condition': primary_condition[0],
            'confidence_score': primary_condition[1],
            'critical_findings': critical_findings,
            'recommendations': self._generate_image_recommendations(image_type, primary_condition, results)
        }
    
    def analyze_health_metrics(self, metrics: Dict) -> Dict:
        """Analyze health metrics and vital signs."""
        alerts = []
        overall_status = 'NORMAL'
        
        for metric_name, value in metrics.items():
            if metric_name in self.critical_vital_ranges:
                ranges = self.critical_vital_ranges[metric_name]
                
                if value < ranges['critical_low'] or value > ranges['critical_high']:
                    alerts.append({
                        'type': 'CRITICAL_VITALS',
                        'metric': metric_name,
                        'value': value,
                        'severity': 'CRITICAL',
                        'message': f'{metric_name.replace("_", " ").title()}: {value} is critically abnormal'
                    })
                    overall_status = 'CRITICAL'
                elif value < ranges['min'] or value > ranges['max']:
                    alerts.append({
                        'type': 'CRITICAL_VITALS',
                        'metric': metric_name,
                        'value': value,
                        'severity': 'HIGH',
                        'message': f'{metric_name.replace("_", " ").title()}: {value} is outside normal range'
                    })
                    if overall_status == 'NORMAL':
                        overall_status = 'HIGH'
        
        return {
            'overall_status': overall_status,
            'alerts': alerts,
            'recommendations': self._generate_health_recommendations(metrics, alerts)
        }
    
    def _create_emergency_alert(self, symptoms: List[str], urgency_level: str) -> Dict:
        """Create emergency alert based on symptoms."""
        return {
            'type': 'SEVERE_SYMPTOMS',
            'severity': urgency_level,
            'message': f'Critical symptoms detected: {", ".join(symptoms)}. Seek immediate medical attention.',
            'actions': [
                'Call emergency services immediately',
                'Go to nearest emergency room',
                'Do not delay seeking medical help'
            ]
        }
    
    def _generate_recommendations(self, diseases: List, urgency_level: str) -> List[str]:
        """Generate recommendations based on diagnosis."""
        recommendations = []
        
        if urgency_level == 'EMERGENCY':
            recommendations.extend([
                'Seek immediate emergency medical care',
                'Call emergency services (911/112)',
                'Go to nearest emergency room'
            ])
        elif urgency_level == 'HIGH':
            recommendations.extend([
                'Seek medical attention within 24 hours',
                'Contact your primary care physician',
                'Consider urgent care if symptoms worsen'
            ])
        elif urgency_level == 'MEDIUM':
            recommendations.extend([
                'Schedule appointment with doctor within a week',
                'Monitor symptoms for changes',
                'Consider over-the-counter treatments if appropriate'
            ])
        else:
            recommendations.extend([
                'Monitor symptoms',
                'Schedule routine checkup if symptoms persist',
                'Practice self-care and rest'
            ])
        
        # Add disease-specific recommendations
        if diseases:
            top_disease = diseases[0][0]
            if 'heart' in top_disease.lower() or 'chest' in top_disease.lower():
                recommendations.append('Avoid strenuous activity until evaluated by doctor')
            elif 'fever' in top_disease.lower():
                recommendations.append('Stay hydrated and rest')
            elif 'pain' in top_disease.lower():
                recommendations.append('Avoid activities that worsen pain')
        
        return recommendations
    
    def _generate_image_analysis_text(self, image_type: str, primary_condition: Tuple, results: Dict) -> str:
        """Generate human-readable analysis text for medical images."""
        condition, confidence = primary_condition
        
        if condition == 'normal':
            return f"The {image_type.lower()} appears to be within normal limits. No significant abnormalities detected."
        
        confidence_percent = int(confidence * 100)
        
        if confidence_percent > 80:
            certainty = "highly suggestive"
        elif confidence_percent > 60:
            certainty = "suggestive"
        else:
            certainty = "possibly suggestive"
        
        return f"The {image_type.lower()} shows findings {certainty} of {condition.replace('_', ' ')}. " \
               f"Confidence level: {confidence_percent}%. " \
               f"Clinical correlation and further evaluation recommended."
    
    def _check_critical_image_findings(self, image_type: str, primary_condition: Tuple, results: Dict) -> List[Dict]:
        """Check for critical findings in medical images."""
        critical_findings = []
        condition, confidence = primary_condition
        
        critical_conditions = {
            'XRAY': ['pneumonia', 'tuberculosis', 'fracture'],
            'MRI': ['tumor', 'stroke'],
            'CT': ['appendicitis', 'aneurysm'],
            'ECG': ['myocardial_infarction', 'heart_block']
        }
        
        if image_type in critical_conditions and condition in critical_conditions[image_type]:
            if confidence > 0.5:  # Only alert if confidence is reasonable
                critical_findings.append({
                    'condition': condition,
                    'confidence': confidence,
                    'urgency': 'HIGH',
                    'message': f'Critical finding detected: {condition.replace("_", " ")}'
                })
        
        return critical_findings
    
    def _generate_image_recommendations(self, image_type: str, primary_condition: Tuple, results: Dict) -> List[str]:
        """Generate recommendations based on image analysis."""
        condition, confidence = primary_condition
        recommendations = []
        
        if condition == 'normal':
            recommendations.append('Continue routine follow-up as recommended by your physician')
        else:
            recommendations.extend([
                'Schedule follow-up with your doctor to discuss findings',
                'Bring this report to your next medical appointment',
                'Follow any specific instructions provided by your healthcare provider'
            ])
            
            if confidence < 0.7:
                recommendations.append('Consider additional imaging or tests for confirmation')
        
        return recommendations
    
    def _generate_health_recommendations(self, metrics: Dict, alerts: List[Dict]) -> List[str]:
        """Generate health recommendations based on metrics and alerts."""
        recommendations = []
        
        if not alerts:
            recommendations.append('Your vital signs are within normal ranges. Continue healthy lifestyle habits.')
            return recommendations
        
        for alert in alerts:
            if alert['severity'] == 'CRITICAL':
                recommendations.append('Seek immediate medical attention')
                recommendations.append('Do not delay - these values require urgent evaluation')
            elif alert['severity'] == 'HIGH':
                recommendations.append('Contact your doctor within 24 hours')
                recommendations.append('Monitor for any worsening symptoms')
            else:
                recommendations.append('Schedule routine checkup to discuss these values')
        
        return recommendations

class DoctorRecommendationService:
    """Service for recommending doctors and hospitals based on diagnosis."""
    
    def get_recommendations(self, diagnosis: Dict, location: str = None) -> Dict:
        """Get doctor and hospital recommendations based on AI diagnosis."""
        recommendations = {
            'doctors': [],
            'hospitals': [],
            'specializations': []
        }
        
        # Get primary disease and symptoms
        if 'possible_diseases' in diagnosis and diagnosis['possible_diseases']:
            primary_disease = diagnosis['possible_diseases'][0][0]
            
            # Find relevant specializations
            specializations = self._find_relevant_specializations(primary_disease)
            recommendations['specializations'] = specializations
            
            # Find doctors with relevant specializations
            doctors = self._find_doctors_by_specializations(specializations, location)
            recommendations['doctors'] = doctors
            
            # Find hospitals with relevant departments
            hospitals = self._find_hospitals_by_specializations(specializations, location)
            recommendations['hospitals'] = hospitals
        
        return recommendations
    
    def _find_relevant_specializations(self, disease_name: str) -> List[str]:
        """Find relevant medical specializations for a disease."""
        disease_specialization_mapping = {
            'heart': ['Cardiology', 'Cardiothoracic Surgery'],
            'chest': ['Cardiology', 'Pulmonology', 'Thoracic Surgery'],
            'brain': ['Neurology', 'Neurosurgery'],
            'cancer': ['Oncology', 'Radiation Oncology'],
            'bone': ['Orthopedics', 'Orthopedic Surgery'],
            'joint': ['Orthopedics', 'Rheumatology'],
            'lung': ['Pulmonology', 'Thoracic Surgery'],
            'stomach': ['Gastroenterology', 'General Surgery'],
            'kidney': ['Nephrology', 'Urology'],
            'eye': ['Ophthalmology'],
            'ear': ['ENT', 'Otolaryngology'],
            'skin': ['Dermatology'],
            'mental': ['Psychiatry', 'Psychology'],
            'child': ['Pediatrics', 'Pediatric Surgery'],
            'woman': ['Gynecology', 'Obstetrics'],
        }
        
        relevant_specializations = []
        disease_lower = disease_name.lower()
        
        for keyword, specs in disease_specialization_mapping.items():
            if keyword in disease_lower:
                relevant_specializations.extend(specs)
        
        # Remove duplicates and return
        return list(set(relevant_specializations))
    
    def _find_doctors_by_specializations(self, specializations: List[str], location: str = None) -> List[Dict]:
        """Find doctors with relevant specializations."""
        doctors = []
        
        for spec_name in specializations:
            try:
                spec = Specialization.objects.get(name=spec_name)
                doctor_query = Doctor.objects.filter(specializations=spec, is_available=True)
                
                if location:
                    doctor_query = doctor_query.filter(
                        hospital__user__profile__address__icontains=location
                    )
                
                for doctor in doctor_query.select_related('hospital')[:5]:  # Limit to 5 per specialization
                    doctors.append({
                        'id': doctor.id,
                        'name': doctor.name,
                        'qualification': doctor.qualification,
                        'experience_years': doctor.experience_years,
                        'consultation_fee': doctor.consultation_fee,
                        'hospital_name': doctor.hospital.hospital_name,
                        'specialization': spec_name,
                        'rating': getattr(doctor, 'average_rating', 0)
                    })
            except Specialization.DoesNotExist:
                continue
        
        # Sort by experience and rating
        doctors.sort(key=lambda x: (x['experience_years'], x['rating']), reverse=True)
        return doctors[:10]  # Return top 10 overall
    
    def _find_hospitals_by_specializations(self, specializations: List[str], location: str = None) -> List[Dict]:
        """Find hospitals with relevant departments."""
        hospitals = []
        
        for spec_name in specializations:
            try:
                spec = Specialization.objects.get(name=spec_name)
                hospital_query = HospitalProfile.objects.filter(
                    doctors__specializations=spec
                ).distinct()
                
                if location:
                    hospital_query = hospital_query.filter(
                        user__profile__address__icontains=location
                    )
                
                for hospital in hospital_query[:5]:  # Limit to 5 per specialization
                    hospitals.append({
                        'id': hospital.id,
                        'name': hospital.hospital_name,
                        'type': getattr(hospital, 'hospital_type', 'Multi-Specialty'),
                        'address': hospital.user.profile.address,
                        'rating': getattr(hospital, 'average_rating', 0),
                        'specialization': spec_name
                    })
            except Specialization.DoesNotExist:
                continue
        
        # Sort by rating
        hospitals.sort(key=lambda x: x['rating'], reverse=True)
        return hospitals[:10]  # Return top 10 overall
