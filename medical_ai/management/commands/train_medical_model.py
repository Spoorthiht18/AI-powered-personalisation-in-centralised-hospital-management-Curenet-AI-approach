"""
Django management command to train the medical diagnosis model
"""

from django.core.management.base import BaseCommand
from medical_ai.training_script import MedicalImageTrainer
import os

class Command(BaseCommand):
    help = 'Train the medical image diagnosis model'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--data-dir',
            type=str,
            default='medical_ai/datasets/medical_images',
            help='Path to the medical images dataset directory'
        )
        parser.add_argument(
            '--image-size',
            type=int,
            nargs=2,
            default=[64, 64],
            help='Image size (width height)'
        )
        parser.add_argument(
            '--test-size',
            type=float,
            default=0.2,
            help='Test set size (0.0 to 1.0)'
        )
    
    def handle(self, *args, **options):
        data_dir = options['data_dir']
        image_size = tuple(options['image_size'])
        test_size = options['test_size']
        
        self.stdout.write(
            self.style.SUCCESS('Starting medical model training...')
        )
        
        # Check if data directory exists
        if not os.path.exists(data_dir):
            self.stdout.write(
                self.style.ERROR(f'Data directory {data_dir} not found!')
            )
            self.stdout.write(
                self.style.WARNING(
                    'Please organize your medical images in the following structure:\n'
                    'medical_ai/datasets/medical_images/\n'
                    '├── Normal/\n'
                    '├── Pneumonia/\n'
                    '├── COVID-19/\n'
                    '├── Tuberculosis/\n'
                    '├── Lung Cancer/\n'
                    '├── Skin Cancer/\n'
                    '├── Melanoma/\n'
                    '├── Dermatitis/\n'
                    '├── Psoriasis/\n'
                    '└── Eczema/\n'
                )
            )
            return
        
        # Create trainer
        trainer = MedicalImageTrainer(image_size=image_size)
        
        try:
            # Load data
            self.stdout.write('Loading data...')
            X, y = trainer.load_data(data_dir)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Found {len(trainer.class_names)} classes: {trainer.class_names}'
                )
            )
            self.stdout.write(f'Total samples: {len(X)}')
            
            # Split data
            from sklearn.model_selection import train_test_split
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42, stratify=y
            )
            
            # Create model
            self.stdout.write('Creating model...')
            trainer.create_model()
            
            # Train model
            self.stdout.write('Training model...')
            history = trainer.train(X_train, X_test, y_train, y_test)
            
            # Evaluate model
            self.stdout.write('Evaluating model...')
            results = trainer.evaluate(history['X_test'], history['y_test'])
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Training Accuracy: {history["train_accuracy"]:.4f}'
                )
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'Test Accuracy: {history["test_accuracy"]:.4f}'
                )
            )
            
            # Save model
            trainer.save_model()
            
            self.stdout.write(
                self.style.SUCCESS('Training completed successfully!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Training failed: {str(e)}')
            )
            raise
