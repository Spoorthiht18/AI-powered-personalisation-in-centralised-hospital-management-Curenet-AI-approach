# Live Disease Diagnosis with AI - Complete Setup Guide

## 🎯 **Overview**

This feature adds **real-time disease diagnosis** from live camera capture to your CureNet AI project. Users can point their camera at affected areas and get instant AI-powered medical analysis.

## 🚀 **Features Implemented**

### **1. Live Camera Capture**
- **Real-time video feed** using device camera
- **Instant photo capture** with one click
- **Mobile-optimized** interface with back camera support
- **Permission handling** for camera access

### **2. AI Disease Detection**
- **10+ Disease Classes**: Normal, Pneumonia, COVID-19, Tuberculosis, Lung Cancer, Skin Cancer, Melanoma, Dermatitis, Psoriasis, Eczema
- **Transfer Learning**: Uses MobileNetV2 for efficient mobile inference
- **Confidence Scoring**: Shows prediction confidence levels
- **Top Predictions**: Displays multiple possible diagnoses

### **3. Medical Recommendations**
- **Instant Recommendations**: AI-generated medical advice
- **Emergency Detection**: Identifies urgent medical situations
- **Severity Assessment**: Categorizes conditions by urgency
- **Professional Guidance**: Suggests when to see a doctor

### **4. Data Management**
- **Diagnosis History**: Complete record of all diagnoses
- **Image Storage**: Secure storage of captured images
- **User Privacy**: All data tied to user accounts
- **Export Options**: Download diagnosis reports

## 🛠 **Technical Implementation**

### **Model Architecture**
```python
# Transfer Learning with MobileNetV2
base_model = MobileNetV2(weights='imagenet', include_top=False)
model = Sequential([
    base_model,
    GlobalAveragePooling2D(),
    Dropout(0.2),
    Dense(128, activation='relu'),
    Dropout(0.2),
    Dense(64, activation='relu'),
    Dense(10, activation='softmax')  # 10 disease classes
])
```

### **Real-time Processing Pipeline**
1. **Camera Capture** → **Image Preprocessing** → **AI Analysis** → **Results Display**
2. **Base64 Encoding** for web transmission
3. **OpenCV Processing** for image optimization
4. **TensorFlow Inference** for disease prediction

## 📋 **Setup Instructions**

### **1. Install Additional Dependencies**

```bash
# Install ML dependencies
pip install tensorflow==2.13.0
pip install opencv-python==4.8.0.76
pip install pillow==10.0.0
pip install matplotlib==3.7.2
pip install seaborn==0.12.2
pip install scikit-learn==1.3.0
```

### **2. Create Model Directory**

```bash
mkdir -p medical_ai/models
mkdir -p medical_ai/datasets/medical_images
```

### **3. Prepare Training Data**

Organize your medical images in this structure:

```
medical_ai/datasets/medical_images/
├── Normal/
│   ├── image1.jpg
│   ├── image2.jpg
│   └── ...
├── Pneumonia/
│   ├── image1.jpg
│   ├── image2.jpg
│   └── ...
├── COVID-19/
│   ├── image1.jpg
│   ├── image2.jpg
│   └── ...
├── Tuberculosis/
│   ├── image1.jpg
│   └── ...
├── Lung Cancer/
│   ├── image1.jpg
│   └── ...
├── Skin Cancer/
│   ├── image1.jpg
│   └── ...
├── Melanoma/
│   ├── image1.jpg
│   └── ...
├── Dermatitis/
│   ├── image1.jpg
│   └── ...
├── Psoriasis/
│   ├── image1.jpg
│   └── ...
└── Eczema/
    ├── image1.jpg
    └── ...
```

### **4. Train the Model**

```bash
# Train with default settings
python manage.py train_medical_model

# Train with custom settings
python manage.py train_medical_model \
    --data-dir medical_ai/datasets/medical_images \
    --epochs 100 \
    --fine-tune-epochs 20 \
    --batch-size 16 \
    --image-size 224 224 \
    --base-model mobilenet
```

### **5. Run Database Migrations**

```bash
python manage.py makemigrations medical_ai
python manage.py migrate
```

## 🎮 **Usage Guide**

### **For Users**

1. **Access Live Diagnosis**:
   - Go to `/ai-diagnosis/live-diagnosis/`
   - Allow camera permissions when prompted

2. **Capture & Diagnose**:
   - Point camera at affected area
   - Click "Capture & Diagnose" button
   - Wait for AI analysis (2-3 seconds)

3. **View Results**:
   - See predicted disease with confidence score
   - Read medical recommendations
   - View alternative diagnoses

4. **Upload Alternative**:
   - Use "Upload Image" option for existing photos
   - Same AI analysis for uploaded images

### **For Developers**

1. **API Endpoints**:
   ```python
   # Live capture diagnosis
   POST /ai-diagnosis/capture-and-diagnose/
   
   # Upload image diagnosis
   POST /ai-diagnosis/upload-and-diagnose/
   
   # Get diagnosis history
   GET /ai-diagnosis/diagnosis-history/
   
   # Train model
   POST /ai-diagnosis/train-model/
   ```

2. **Model Training**:
   ```python
   from medical_ai.training_script import MedicalImageTrainer
   
   trainer = MedicalImageTrainer()
   trainer.create_model()
   trainer.train(train_gen, val_gen, epochs=50)
   trainer.save_model()
   ```

## 🔧 **Configuration Options**

### **Model Settings**
```python
# In live_diagnosis.py
IMAGE_SIZE = (224, 224)  # Input image size
CONFIDENCE_THRESHOLD = 0.7  # Minimum confidence for diagnosis
BATCH_SIZE = 32  # Training batch size
```

### **Disease Classes**
```python
# Add new diseases in live_diagnosis.py
self.class_names = [
    'Normal', 'Pneumonia', 'COVID-19', 'Tuberculosis', 'Lung Cancer',
    'Skin Cancer', 'Melanoma', 'Dermatitis', 'Psoriasis', 'Eczema',
    'Your New Disease'  # Add here
]
```

### **Recommendations**
```python
# Customize recommendations in get_recommendations()
recommendations = {
    'Your Disease': [
        "Custom recommendation 1",
        "Custom recommendation 2",
        "Custom recommendation 3"
    ]
}
```

## 📊 **Performance Optimization**

### **Model Optimization**
- **Quantization**: Reduce model size for mobile deployment
- **Pruning**: Remove unnecessary connections
- **Knowledge Distillation**: Train smaller student model

### **Inference Optimization**
- **Batch Processing**: Process multiple images together
- **Caching**: Cache model predictions
- **GPU Acceleration**: Use GPU for faster inference

## 🚨 **Important Considerations**

### **Medical Disclaimer**
- **Not a Replacement**: This is not a replacement for professional medical diagnosis
- **Emergency Situations**: Always seek immediate medical help for emergencies
- **Accuracy Limitations**: AI predictions should be used as guidance only
- **Professional Consultation**: Always consult healthcare professionals

### **Privacy & Security**
- **Data Encryption**: All images are encrypted in transit and storage
- **User Consent**: Clear consent for camera and image usage
- **Data Retention**: Configurable data retention policies
- **GDPR Compliance**: European data protection compliance

### **Legal Requirements**
- **Medical Device Regulations**: May require medical device certification
- **FDA Approval**: Consider FDA approval for medical AI systems
- **Liability Insurance**: Professional liability insurance recommended
- **Terms of Service**: Clear terms regarding AI diagnosis limitations

## 🔮 **Future Enhancements**

### **Advanced Features**
- **3D Image Analysis**: Support for 3D medical images
- **Video Analysis**: Real-time video stream analysis
- **Multi-modal Input**: Combine image + text symptoms
- **Telemedicine Integration**: Direct doctor consultation

### **AI Improvements**
- **Federated Learning**: Train on distributed data
- **Active Learning**: Improve model with user feedback
- **Ensemble Methods**: Combine multiple AI models
- **Explainable AI**: Show why AI made specific predictions

## 🐛 **Troubleshooting**

### **Common Issues**

1. **Camera Not Working**:
   - Check browser permissions
   - Ensure HTTPS connection
   - Try different browser

2. **Model Loading Errors**:
   - Check model file exists
   - Verify TensorFlow installation
   - Check file permissions

3. **Low Accuracy**:
   - Add more training data
   - Increase training epochs
   - Try different base model

4. **Slow Performance**:
   - Reduce image size
   - Use GPU acceleration
   - Optimize model architecture

### **Debug Mode**
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📈 **Monitoring & Analytics**

### **Performance Metrics**
- **Accuracy**: Model prediction accuracy
- **Response Time**: API response times
- **Usage Statistics**: User engagement metrics
- **Error Rates**: System error tracking

### **Health Monitoring**
- **Model Drift**: Monitor prediction quality over time
- **Data Quality**: Track input image quality
- **User Feedback**: Collect user satisfaction scores
- **System Health**: Monitor server performance

---

**Your CureNet AI now has cutting-edge live disease diagnosis capabilities! 🎉**

The system is ready for training and deployment. Follow the setup instructions to get started with your own medical image dataset.
