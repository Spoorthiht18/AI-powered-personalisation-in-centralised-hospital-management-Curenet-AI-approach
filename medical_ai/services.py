import numpy as np
from PIL import Image
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from .models import MedicalReport, DiagnosisSession, Disease, Symptom

class MedicalImageAnalyzer:
    def __init__(self):
        # Initialize a simple model for medical image analysis
        self.model = RandomForestClassifier(n_estimators=100)
        self.scaler = StandardScaler()
        
    def _create_simple_model(self):
        # Train the model with some initial data (you would need to provide real training data)
        # This is just a placeholder
        X = np.random.rand(100, 128*128*3)  # Random training data
        y = np.random.randint(0, 2, 100)    # Random labels
        
        # Scale the features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train the model
        self.model.fit(X_scaled, y)
        return self.model
        
    def preprocess_image(self, image):
        if isinstance(image, str):
            image = Image.open(image)
        # Resize image to standard size
        image = image.resize((128, 128))
        # Convert to numpy array and flatten
        image_array = np.array(image).reshape(1, -1)
        # Scale the features
        image_array_scaled = self.scaler.transform(image_array)
        return image_array_scaled
    
    def analyze_image(self, image):
        preprocessed_image = self.preprocess_image(image)
        predictions = self.model.predict(preprocessed_image)
        return self._interpret_predictions(predictions)
    
    def _interpret_predictions(self, predictions):
        # Simple binary classification interpretation
        abnormal_prob = float(predictions[0][1])
        return {
            'abnormality_detected': abnormal_prob > 0.5,
            'confidence_score': abnormal_prob,
            'recommendations': self._generate_recommendations(abnormal_prob)
        }
    
    def _generate_recommendations(self, abnormal_prob):
        recommendations = []
        if abnormal_prob > 0.7:
            recommendations.append("Urgent: Please consult with a specialist immediately")
        elif abnormal_prob > 0.5:
            recommendations.append("Recommended: Schedule a follow-up with a specialist")
        else:
            recommendations.append("No immediate concerns detected, but consult with your doctor for confirmation")
        return recommendations

class SymptomAnalyzer:
    def __init__(self):
        self.classifier = RandomForestClassifier(n_estimators=100)
        
    def train_model(self):
        # Get all symptoms and diseases
        symptoms = Symptom.objects.all()
        diseases = Disease.objects.all()
        
        # Prepare training data
        X = []  # Symptom vectors
        y = []  # Disease labels
        
        for disease in diseases:
            disease_symptoms = disease.symptoms.all()
            symptom_vector = [1 if symptom in disease_symptoms else 0 for symptom in symptoms]
            X.append(symptom_vector)
            y.append(disease.id)
        
        # Train the classifier
        self.classifier.fit(X, y)
    
    def predict_disease(self, symptoms):
        # Convert symptoms to feature vector
        all_symptoms = Symptom.objects.all()
        symptom_vector = [1 if symptom in symptoms else 0 for symptom in all_symptoms]
        
        # Get prediction probabilities
        disease_probabilities = self.classifier.predict_proba([symptom_vector])[0]
        
        # Get top 3 most likely diseases
        top_indices = np.argsort(disease_probabilities)[-3:][::-1]
        diseases = Disease.objects.filter(id__in=self.classifier.classes_[top_indices])
        
        return [
            {
                'disease': disease.name,
                'probability': float(disease_probabilities[list(self.classifier.classes_).index(disease.id)]),
                'description': disease.description
            }
            for disease in diseases
        ]

class ReportAnalyzer:
    def analyze_report(self, report):
        # Add custom report analysis logic here
        # This could include:
        # - Text extraction from PDFs
        # - Lab value analysis
        # - Trend analysis
        pass

# Initialize global analyzer instances
image_analyzer = MedicalImageAnalyzer()
symptom_analyzer = SymptomAnalyzer()
report_analyzer = ReportAnalyzer()

def analyze_medical_report(report_id):
    """Analyze a medical report using AI"""
    report = MedicalReport.objects.get(id=report_id)
    
    # Analyze based on report type
    if report.report_type in ['XRAY', 'MRI', 'CT']:
        analysis = image_analyzer.analyze_image(report.report_file.path)
    else:
        analysis = report_analyzer.analyze_report(report.report_file.path)
    
    # Save analysis results
    report.ai_analysis_result = analysis
    report.analysis_complete = True
    report.save()
    
    return analysis

def predict_disease_from_symptoms(session_id):
    """Predict possible diseases based on reported symptoms"""
    session = DiagnosisSession.objects.get(id=session_id)
    symptoms = session.symptoms.all()
    
    # Ensure model is trained
    symptom_analyzer.train_model()
    
    # Get predictions
    predictions = symptom_analyzer.predict_disease(symptoms)
    return predictions

def get_follow_up_questions(session):
    """Generate follow-up questions based on reported symptoms"""
    reported_symptoms = session.symptoms.all()
    
    # Add logic to generate relevant follow-up questions
    # based on the reported symptoms and potential diseases
    
    return [
        "How long have you been experiencing these symptoms?",
        "Have you had any similar symptoms in the past?",
        "Are the symptoms constant or do they come and go?",
        "What makes the symptoms better or worse?",
    ]

def analyze_image_report(image_file):
    """Analyze medical images using AI"""
    return image_analyzer.analyze_image(image_file)
