"""
Live Medical Image Diagnosis System
Real-time disease detection from camera capture
"""

import numpy as np
import json
import logging
from typing import Dict, List, Tuple
import base64
from io import BytesIO
from PIL import Image
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import pickle
import os

logger = logging.getLogger(__name__)

class LiveMedicalDiagnosis:
    """Real-time medical image diagnosis system"""
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.class_names = []
        self.confidence_threshold = 0.7
        self.image_size = (64, 64)  # Smaller size for faster processing
        self.load_model()
        
    def load_model(self):
        """Load or create the medical diagnosis model"""
        try:
            # Try to load pre-trained model
            with open('medical_ai/models/disease_model.pkl', 'rb') as f:
                self.model = pickle.load(f)
            with open('medical_ai/models/scaler.pkl', 'rb') as f:
                self.scaler = pickle.load(f)
            with open('medical_ai/models/class_names.json', 'r') as f:
                self.class_names = json.load(f)
            logger.info("Pre-trained model loaded successfully")
        except:
            # Create new model if none exists
            self.create_model()
            logger.info("New model created")
    
    def create_model(self):
        """Create a new medical diagnosis model"""
        # Use Random Forest for simplicity and reliability
        self.model = RandomForestClassifier(
            n_estimators=100,
            random_state=42,
            max_depth=10,
            min_samples_split=5
        )
        
        # Create scaler for feature normalization
        self.scaler = StandardScaler()
        
        # Default disease classes
        self.class_names = [
            'Normal', 'Pneumonia', 'COVID-19', 'Tuberculosis', 'Lung Cancer',
            'Skin Cancer', 'Melanoma', 'Dermatitis', 'Psoriasis', 'Eczema'
        ]
        
        # Save class names
        os.makedirs('medical_ai/models', exist_ok=True)
        with open('medical_ai/models/class_names.json', 'w') as f:
            json.dump(self.class_names, f)
    
    def extract_features(self, image: np.ndarray) -> np.ndarray:
        """Extract features from image for ML model"""
        try:
            # Convert PIL Image to numpy array if needed
            if isinstance(image, Image.Image):
                image = np.array(image)
            
            # Resize image using PIL
            if len(image.shape) == 3:
                pil_image = Image.fromarray(image)
                pil_image = pil_image.resize(self.image_size)
                image = np.array(pil_image)
            
            # Convert to grayscale for simplicity
            if len(image.shape) == 3:
                # Convert to grayscale
                gray_image = np.dot(image[...,:3], [0.2989, 0.5870, 0.1140])
            else:
                gray_image = image
            
            # Flatten the image to 1D feature vector
            features = gray_image.flatten()
            
            # Add some basic statistical features
            mean_val = np.mean(gray_image)
            std_val = np.std(gray_image)
            min_val = np.min(gray_image)
            max_val = np.max(gray_image)
            
            # Combine image features with statistical features
            statistical_features = np.array([mean_val, std_val, min_val, max_val])
            features = np.concatenate([features, statistical_features])
            
            return features
        except Exception as e:
            logger.error(f"Error extracting features: {e}")
            return None
    
    def predict_disease(self, image: np.ndarray) -> Dict:
        """Predict disease from image"""
        try:
            # Extract features
            features = self.extract_features(image)
            if features is None:
                return {'error': 'Failed to extract features from image'}
            
            # Reshape for single prediction
            features = features.reshape(1, -1)
            
            # Scale features if scaler is available
            if self.scaler is not None:
                features = self.scaler.transform(features)
            
            # Make prediction
            if self.model is None:
                return {'error': 'Model not loaded'}
            
            # Get prediction probabilities
            prediction_proba = self.model.predict_proba(features)[0]
            predicted_class_idx = np.argmax(prediction_proba)
            confidence = float(prediction_proba[predicted_class_idx])
            
            # Get class name
            if predicted_class_idx < len(self.class_names):
                predicted_class = self.class_names[predicted_class_idx]
            else:
                predicted_class = 'Unknown'
            
            # Check confidence threshold
            if confidence < self.confidence_threshold:
                predicted_class = 'Uncertain'
                confidence = 1.0 - confidence
            
            # Get top 3 predictions
            top_indices = np.argsort(prediction_proba)[-3:][::-1]
            top_predictions = []
            
            for idx in top_indices:
                if idx < len(self.class_names):
                    top_predictions.append({
                        'disease': self.class_names[idx],
                        'confidence': float(prediction_proba[idx])
                    })
            
            return {
                'success': True,
                'predicted_disease': predicted_class,
                'confidence': confidence,
                'top_predictions': top_predictions,
                'recommendations': self.get_recommendations(predicted_class, confidence)
            }
            
        except Exception as e:
            logger.error(f"Error in prediction: {e}")
            return {'error': f'Prediction failed: {str(e)}'}
    
    def get_recommendations(self, disease: str, confidence: float) -> List[str]:
        """Get medical recommendations based on diagnosis"""
        recommendations = {
            'Normal': [
                "No immediate medical concerns detected",
                "Continue regular health checkups",
                "Maintain healthy lifestyle"
            ],
            'Pneumonia': [
                "Seek immediate medical attention",
                "Rest and stay hydrated",
                "Monitor breathing and temperature",
                "Consider chest X-ray for confirmation"
            ],
            'COVID-19': [
                "Isolate immediately and get tested",
                "Monitor symptoms closely",
                "Seek emergency care if breathing difficulties",
                "Follow local health guidelines"
            ],
            'Tuberculosis': [
                "Urgent medical consultation required",
                "Complete diagnostic tests",
                "Follow treatment protocol strictly",
                "Inform close contacts for screening"
            ],
            'Lung Cancer': [
                "Immediate oncologist consultation",
                "Schedule CT scan and biopsy",
                "Consider second opinion",
                "Discuss treatment options"
            ],
            'Skin Cancer': [
                "Dermatologist consultation within 48 hours",
                "Avoid sun exposure",
                "Monitor for changes",
                "Consider biopsy for confirmation"
            ],
            'Melanoma': [
                "URGENT: Dermatologist consultation within 24 hours",
                "Document lesion appearance",
                "Avoid sun exposure completely",
                "Prepare for possible surgical intervention"
            ],
            'Dermatitis': [
                "Avoid irritants and allergens",
                "Use gentle, fragrance-free products",
                "Apply prescribed topical treatments",
                "Monitor for infection signs"
            ],
            'Psoriasis': [
                "Dermatologist consultation",
                "Avoid triggers (stress, alcohol, smoking)",
                "Use moisturizers regularly",
                "Consider phototherapy options"
            ],
            'Eczema': [
                "Keep skin moisturized",
                "Avoid harsh soaps and hot water",
                "Identify and avoid triggers",
                "Use prescribed topical treatments"
            ],
            'Uncertain': [
                "Consult healthcare professional",
                "Provide detailed symptom history",
                "Consider additional diagnostic tests",
                "Monitor for symptom changes"
            ]
        }
        
        return recommendations.get(disease, [
            "Consult healthcare professional",
            "Provide detailed medical history",
            "Consider additional diagnostic tests"
        ])
    
    def train_model(self, training_data_path: str, test_size: float = 0.2):
        """Train the model on medical image dataset"""
        try:
            import os
            from sklearn.model_selection import train_test_split
            
            # Load training data
            X, y = self.load_training_data(training_data_path)
            
            if X is None or len(X) == 0:
                return None
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42, stratify=y
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train model
            self.model.fit(X_train_scaled, y_train)
            
            # Evaluate model
            train_score = self.model.score(X_train_scaled, y_train)
            test_score = self.model.score(X_test_scaled, y_test)
            
            logger.info(f"Training accuracy: {train_score:.4f}")
            logger.info(f"Test accuracy: {test_score:.4f}")
            
            # Save model and scaler
            os.makedirs('medical_ai/models', exist_ok=True)
            with open('medical_ai/models/disease_model.pkl', 'wb') as f:
                pickle.dump(self.model, f)
            with open('medical_ai/models/scaler.pkl', 'wb') as f:
                pickle.dump(self.scaler, f)
            with open('medical_ai/models/class_names.json', 'w') as f:
                json.dump(self.class_names, f)
            
            logger.info("Model trained and saved successfully")
            return {'train_score': train_score, 'test_score': test_score}
            
        except Exception as e:
            logger.error(f"Error training model: {e}")
            return None
    
    def load_training_data(self, data_path: str):
        """Load training data from directory"""
        try:
            import os
            from sklearn.preprocessing import LabelEncoder
            
            X = []
            y = []
            label_encoder = LabelEncoder()
            
            # Get all subdirectories (disease classes)
            disease_classes = [d for d in os.listdir(data_path) 
                             if os.path.isdir(os.path.join(data_path, d))]
            
            self.class_names = disease_classes
            
            for disease in disease_classes:
                disease_path = os.path.join(data_path, disease)
                for filename in os.listdir(disease_path):
                    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                        image_path = os.path.join(disease_path, filename)
                        try:
                            # Load and process image
                            image = Image.open(image_path)
                            image_array = np.array(image)
                            
                            # Extract features
                            features = self.extract_features(image_array)
                            if features is not None:
                                X.append(features)
                                y.append(disease)
                        except Exception as e:
                            logger.warning(f"Error loading image {image_path}: {e}")
                            continue
            
            if len(X) == 0:
                logger.error("No valid images found in training data")
                return None, None
            
            # Encode labels
            y_encoded = label_encoder.fit_transform(y)
            
            return np.array(X), y_encoded
            
        except Exception as e:
            logger.error(f"Error loading training data: {e}")
            return None, None
    
    def process_live_capture(self, image_data: str) -> Dict:
        """Process live camera capture for diagnosis"""
        try:
            # Decode base64 image
            if image_data.startswith('data:image'):
                image_data = image_data.split(',')[1]
            
            image_bytes = base64.b64decode(image_data)
            image = Image.open(BytesIO(image_bytes))
            image = np.array(image)
            
            # Get diagnosis
            result = self.predict_disease(image)
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing live capture: {e}")
            return {'error': f'Failed to process image: {str(e)}'}

# Global instance
live_diagnosis = LiveMedicalDiagnosis()
