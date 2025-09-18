"""
Medical Image Classification Training Script
Train the model on medical image datasets for disease diagnosis
"""

import os
import json
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from PIL import Image
import pickle

class MedicalImageTrainer:
    """Train medical image classification models"""
    
    def __init__(self, image_size=(64, 64)):
        self.image_size = image_size
        self.model = None
        self.scaler = None
        self.label_encoder = None
        self.class_names = []
        
    def extract_features(self, image_path):
        """Extract features from a single image"""
        try:
            # Load image
            image = Image.open(image_path)
            image = image.resize(self.image_size)
            image_array = np.array(image)
            
            # Convert to grayscale
            if len(image_array.shape) == 3:
                gray_image = np.dot(image_array[...,:3], [0.2989, 0.5870, 0.1140])
            else:
                gray_image = image_array
            
            # Flatten image
            features = gray_image.flatten()
            
            # Add statistical features
            mean_val = np.mean(gray_image)
            std_val = np.std(gray_image)
            min_val = np.min(gray_image)
            max_val = np.max(gray_image)
            
            statistical_features = np.array([mean_val, std_val, min_val, max_val])
            features = np.concatenate([features, statistical_features])
            
            return features
        except Exception as e:
            print(f"Error processing {image_path}: {e}")
            return None
    
    def load_data(self, data_dir):
        """Load all training data"""
        X = []
        y = []
        
        # Get all disease classes
        disease_classes = [d for d in os.listdir(data_dir) 
                          if os.path.isdir(os.path.join(data_dir, d))]
        
        self.class_names = sorted(disease_classes)
        
        for disease in self.class_names:
            disease_path = os.path.join(data_dir, disease)
            for filename in os.listdir(disease_path):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    image_path = os.path.join(disease_path, filename)
                    features = self.extract_features(image_path)
                    if features is not None:
                        X.append(features)
                        y.append(disease)
        
        return np.array(X), np.array(y)
    
    def create_model(self):
        """Create the model architecture"""
        # Use Random Forest for simplicity
        self.model = RandomForestClassifier(
            n_estimators=100,
            random_state=42,
            max_depth=10,
            min_samples_split=5,
            n_jobs=-1
        )
        
        # Create scaler and label encoder
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        
        return self.model
    
    def train(self, X_train, X_test, y_train, y_test):
        """Train the model"""
        
        print("Starting training...")
        
        # Encode labels
        y_train_encoded = self.label_encoder.fit_transform(y_train)
        y_test_encoded = self.label_encoder.transform(y_test)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.model.fit(X_train_scaled, y_train_encoded)
        
        # Evaluate
        train_score = self.model.score(X_train_scaled, y_train_encoded)
        test_score = self.model.score(X_test_scaled, y_test_encoded)
        
        print(f"Training accuracy: {train_score:.4f}")
        print(f"Test accuracy: {test_score:.4f}")
        
        return {
            'train_accuracy': train_score,
            'test_accuracy': test_score,
            'y_test': y_test_encoded,
            'X_test': X_test_scaled
        }
    
    def evaluate(self, X_test, y_test):
        """Evaluate the model"""
        
        # Get predictions
        y_pred = self.model.predict(X_test)
        
        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        
        # Classification report
        report = classification_report(
            y_test, y_pred, 
            target_names=self.class_names
        )
        
        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred)
        
        return {
            'accuracy': accuracy,
            'classification_report': report,
            'confusion_matrix': cm,
            'predictions': y_pred
        }
    
    def print_training_summary(self, train_acc, test_acc):
        """Print training summary without plotting"""
        print(f"\n=== Training Summary ===")
        print(f"Training Accuracy: {train_acc:.4f}")
        print(f"Test Accuracy: {test_acc:.4f}")
        print("=" * 30)
    
    def print_confusion_matrix(self, cm):
        """Print confusion matrix without plotting"""
        print(f"\n=== Confusion Matrix ===")
        print("Predicted ->")
        print("Actual")
        print("  ", end="")
        for i, class_name in enumerate(self.class_names):
            print(f"{class_name:>10}", end="")
        print()
        
        for i, class_name in enumerate(self.class_names):
            print(f"{class_name:>10}", end="")
            for j in range(len(self.class_names)):
                print(f"{cm[i][j]:>10}", end="")
            print()
        print("=" * 30)
    
    def save_model(self, model_path='medical_ai/models/disease_model.pkl'):
        """Save the trained model"""
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        # Save model and scaler
        with open(model_path, 'wb') as f:
            pickle.dump(self.model, f)
        
        scaler_path = os.path.join(os.path.dirname(model_path), 'scaler.pkl')
        with open(scaler_path, 'wb') as f:
            pickle.dump(self.scaler, f)
        
        # Save class names
        class_names_path = os.path.join(os.path.dirname(model_path), 'class_names.json')
        with open(class_names_path, 'w') as f:
            json.dump(self.class_names, f)
        
        print(f"Model saved to {model_path}")
        print(f"Scaler saved to {scaler_path}")
        print(f"Class names saved to {class_names_path}")
    
    def load_model(self, model_path='medical_ai/models/disease_model.pkl'):
        """Load a trained model"""
        
        with open(model_path, 'rb') as f:
            self.model = pickle.load(f)
        
        scaler_path = os.path.join(os.path.dirname(model_path), 'scaler.pkl')
        with open(scaler_path, 'rb') as f:
            self.scaler = pickle.load(f)
        
        # Load class names
        class_names_path = os.path.join(os.path.dirname(model_path), 'class_names.json')
        with open(class_names_path, 'r') as f:
            self.class_names = json.load(f)
        
        print(f"Model loaded from {model_path}")
        print(f"Class names: {self.class_names}")

def main():
    """Main training function"""
    
    # Configuration
    DATA_DIR = 'medical_ai/datasets/medical_images'  # Update this path
    IMAGE_SIZE = (64, 64)
    
    # Create trainer
    trainer = MedicalImageTrainer(image_size=IMAGE_SIZE)
    
    # Check if data directory exists
    if not os.path.exists(DATA_DIR):
        print(f"Data directory {DATA_DIR} not found!")
        print("Please organize your medical images in the following structure:")
        print("""
        medical_ai/datasets/medical_images/
        ├── Normal/
        │   ├── image1.jpg
        │   └── image2.jpg
        ├── Pneumonia/
        │   ├── image1.jpg
        │   └── image2.jpg
        ├── COVID-19/
        │   ├── image1.jpg
        │   └── image2.jpg
        └── ... (other disease classes)
        """)
        return
    
    # Load data
    print("Loading data...")
    X, y = trainer.load_data(DATA_DIR)
    
    print(f"Found {len(trainer.class_names)} classes: {trainer.class_names}")
    print(f"Total samples: {len(X)}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Create model
    print("Creating model...")
    trainer.create_model()
    
    # Train model
    print("Training model...")
    history = trainer.train(X_train, X_test, y_train, y_test)
    
    # Print training summary
    trainer.print_training_summary(history['train_accuracy'], history['test_accuracy'])
    
    # Evaluate model
    print("Evaluating model...")
    results = trainer.evaluate(history['X_test'], history['y_test'])
    print(f"Validation Accuracy: {results['accuracy']:.4f}")
    print("\nClassification Report:")
    print(results['classification_report'])
    
    # Print confusion matrix
    trainer.print_confusion_matrix(results['confusion_matrix'])
    
    # Save model
    trainer.save_model()
    
    print("Training completed successfully!")

if __name__ == "__main__":
    main()
