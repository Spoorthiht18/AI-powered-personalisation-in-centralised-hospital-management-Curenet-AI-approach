# CureNet AI - Centralized Hospital Management System

CureNet AI is an AI-powered centralized hospital management system that connects patients with hospitals and doctors through a comprehensive platform.

## Features

- **AI-Powered Chatbot**: 24/7 health assistant that understands symptoms, suggests doctors, and provides medicine information
- **Phone Number Authentication**: Secure login with OTP verification
- **Hospital & Doctor Discovery**: Find healthcare providers based on location, ratings, and specialization
- **Appointment Booking**: Book tokens/appointments with doctors across all registered hospitals
- **Video Consultations**: Connect with doctors through secure video calls
- **Electronic Medical Records**: Maintain complete medical history in one place
- **Home Doctor Visits**: Request doctors to visit your home based on your location
- **Hospital Registration Portal**: Hospitals can register and manage their profiles
- **Admin Dashboard**: Superuser access for platform management

## Tech Stack

- **Backend**: Django, Django REST Framework
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Database**: SQLite (Development), PostgreSQL (Production)
- **Authentication**: Phone number-based OTP verification
- **AI Integration**: Machine learning models for symptom analysis and recommendations
- **Location Services**: Geolocation for nearest hospital suggestions
- **Video Calls**: WebRTC for secure video consultations

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/curenet-ai.git
   cd curenet-ai
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables (create a `.env` file in the root directory):
   ```
   SECRET_KEY=your_secret_key
   DEBUG=True
   AI_MODEL_API_KEY=your_ai_model_api_key
   AI_MODEL_ENDPOINT=your_ai_model_endpoint
   ```

5. Run migrations:
   ```
   python manage.py makemigrations
   python manage.py migrate
   ```

6. Create a superuser:
   ```
   python manage.py createsuperuser
   ```

7. Run the development server:
   ```
   python manage.py runserver
   ```

8. Access the application at http://127.0.0.1:8000/

## Project Structure

```
curenet_ai/
├── accounts/            # User authentication and profiles
├── appointments/        # Appointment booking and management
├── chatbot/             # AI chatbot implementation
├── curenet_ai/          # Project settings and main URLs
├── hospitals/           # Hospital and doctor management
├── media/               # User-uploaded files
├── static/              # Static assets
│   ├── css/             # CSS stylesheets
│   ├── js/              # JavaScript files
│   └── images/          # Image assets
└── templates/           # HTML templates
    ├── accounts/        # Authentication templates
    ├── appointments/    # Appointment templates
    ├── base/            # Base templates
    ├── chatbot/         # Chatbot templates
    └── hospitals/       # Hospital templates
```

## User Types

- **Patients**: Regular users who can book appointments, chat with AI, and maintain their medical records
- **Hospitals**: Healthcare providers who can register their facilities, manage doctors, and handle appointments
- **Admin**: Superusers who manage the platform and approve hospital registrations

## API Endpoints

The application provides a comprehensive REST API for all functionality:

- `/api/accounts/`: User authentication and profile management
- `/api/hospitals/`: Hospital and doctor data
- `/api/appointments/`: Appointment booking and management
- `/api/chatbot/`: AI chatbot interactions

## Contributions

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

For any inquiries, please contact support@curenetai.com 