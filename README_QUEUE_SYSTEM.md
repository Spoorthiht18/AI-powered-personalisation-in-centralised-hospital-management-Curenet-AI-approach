# Real-Time Queue System for CureNet AI

This document explains how to set up and use the real-time queue system for hospital token booking in the CureNet AI application.

## Features

- **Real-time Queue Management**: Live updates using WebSockets
- **Token Generation**: Automatic token numbering for each hospital
- **Priority System**: Support for Normal, Urgent, and Emergency priorities
- **Status Tracking**: Waiting, Calling, In Progress, Completed, Cancelled
- **Live Statistics**: Real-time count of tokens in different statuses
- **Hospital & Doctor Selection**: Choose specific hospital and doctor
- **Estimated Wait Times**: Display estimated waiting time for patients

## Prerequisites

1. **Redis Server**: Required for Django Channels
2. **Python Dependencies**: Django Channels and related packages
3. **Database**: SQLite (default) or PostgreSQL/MySQL

## Installation & Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install and Start Redis

**Windows:**
```bash
# Download Redis for Windows from https://github.com/microsoftarchive/redis/releases
# Or use WSL2 with Ubuntu and install Redis there

# Using WSL2 (recommended):
wsl --install Ubuntu
wsl -d Ubuntu
sudo apt update
sudo apt install redis-server
sudo service redis-server start
```

**macOS:**
```bash
brew install redis
brew services start redis
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

### 3. Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Create Sample Data

```bash
# Create a superuser first
python manage.py createsuperuser

# Populate sample hospitals and doctors (if not already done)
python manage.py import_hospitals

# Create sample queue tokens for testing
python manage.py populate_queue
```

### 5. Run the Development Server

```bash
# For development with WebSocket support
python manage.py runserver

# For production, use Daphne or uvicorn with ASGI
daphne curenet_ai.asgi:application
```

## Usage

### For Patients

1. **Navigate to Appointments**: Go to "My Appointments" page
2. **Select Queue System Tab**: Click on the "Queue System" tab
3. **Choose Hospital**: Select a hospital from the dropdown
4. **Choose Doctor**: Select a doctor (optional but recommended)
5. **Get Token**: Click "Get Token" button to receive a queue token
6. **Monitor Queue**: Watch real-time updates of your position in the queue

### For Hospital Staff

1. **Admin Panel**: Access Django admin at `/admin/`
2. **Queue Management**: Navigate to "Queue tokens" section
3. **Update Status**: Change token status (Waiting → Calling → In Progress → Completed)
4. **Priority Management**: Adjust priority levels for urgent cases
5. **Real-time Updates**: All changes are reflected immediately in the patient interface

## API Endpoints

### Queue Token Management

- `POST /api/queue-tokens/` - Create a new queue token
- `GET /api/queue-tokens/my-tokens/` - Get user's active tokens
- `POST /api/queue-tokens/{id}/cancel/` - Cancel a token

### WebSocket Endpoints

- `ws://localhost:8000/ws/queue/{hospital_id}/` - Real-time queue updates

## Technical Architecture

### Models

- **QueueToken**: Main model for queue management
  - Token number, patient, doctor, hospital
  - Status tracking (Waiting, Calling, In Progress, Completed, Cancelled)
  - Priority levels (Normal, Urgent, Emergency)
  - Timestamps for various events

### WebSocket Implementation

- **Django Channels**: ASGI application with WebSocket support
- **Redis Backend**: Channel layer for real-time communication
- **Consumer Pattern**: Async WebSocket consumers for each hospital

### Frontend

- **Vanilla JavaScript**: No external framework dependencies
- **Bootstrap 5**: Responsive UI components
- **Real-time Updates**: Live queue status without page refresh

## Configuration

### Settings

```python
# curenet_ai/settings.py

INSTALLED_APPS = [
    # ... other apps
    'channels',
]

# Django Channels Configuration
ASGI_APPLICATION = 'curenet_ai.asgi.application'

# Channel Layers for Redis backend
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}
```

### ASGI Configuration

```python
# curenet_ai/asgi.py

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from appointments.routing import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'curenet_ai.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
```

## Customization

### Adding New Statuses

1. Update `TOKEN_STATUS` choices in `QueueToken` model
2. Add corresponding CSS classes in JavaScript
3. Update admin interface if needed

### Priority Levels

1. Modify `PRIORITY` choices in the model
2. Update JavaScript badge styling
3. Adjust queue ordering logic

### Estimated Wait Times

1. Implement dynamic calculation based on:
   - Number of people ahead in queue
   - Average consultation time
   - Doctor availability
   - Priority levels

## Troubleshooting

### Common Issues

1. **WebSocket Connection Failed**
   - Check if Redis is running
   - Verify ASGI configuration
   - Check browser console for errors

2. **Real-time Updates Not Working**
   - Ensure WebSocket connection is established
   - Check Redis connection in Django
   - Verify consumer routing

3. **Token Generation Errors**
   - Check database migrations
   - Verify user authentication
   - Check API endpoint permissions

### Debug Mode

```python
# settings.py
DEBUG = True

# Enable Django Channels debug logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'channels': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

## Production Deployment

### Requirements

1. **Redis Cluster**: For high availability
2. **ASGI Server**: Daphne, uvicorn, or hypercorn
3. **Load Balancer**: For multiple server instances
4. **SSL/TLS**: Secure WebSocket connections

### Environment Variables

```bash
# .env
REDIS_URL=redis://localhost:6379/0
CHANNEL_LAYERS_BACKEND=channels_redis.core.RedisChannelLayer
DJANGO_SETTINGS_MODULE=curenet_ai.settings
```

### Docker Support

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Install Redis
RUN apt-get update && apt-get install -y redis-server

# ... rest of Dockerfile
```

## Security Considerations

1. **Authentication**: WebSocket connections require user authentication
2. **Authorization**: Users can only access their own tokens
3. **CSRF Protection**: API endpoints include CSRF validation
4. **Rate Limiting**: Consider implementing API rate limiting
5. **Input Validation**: All user inputs are validated and sanitized

## Performance Optimization

1. **Database Indexing**: Index on frequently queried fields
2. **Redis Caching**: Cache frequently accessed queue data
3. **Connection Pooling**: Optimize database connections
4. **Async Operations**: Use async/await for I/O operations
5. **Pagination**: Limit results for large datasets

## Monitoring & Analytics

### Metrics to Track

1. **Queue Length**: Average waiting time
2. **Token Processing**: Time from creation to completion
3. **User Engagement**: Active users in queue system
4. **System Performance**: WebSocket connection stability

### Logging

```python
# Add to views and consumers
import logging
logger = logging.getLogger(__name__)

logger.info(f"Token {token.id} status changed to {new_status}")
logger.error(f"Failed to create token: {error}")
```

## Future Enhancements

1. **Mobile App**: Native mobile applications
2. **Push Notifications**: SMS/Email alerts for token updates
3. **AI Integration**: Smart queue optimization
4. **Multi-language Support**: Internationalization
5. **Analytics Dashboard**: Advanced reporting and insights
6. **Integration APIs**: Connect with external hospital systems

## Support

For technical support or questions:

1. Check the Django Channels documentation
2. Review Django logs for error messages
3. Verify Redis server status
4. Test WebSocket connections using browser dev tools

## License

This queue system is part of the CureNet AI project and follows the same licensing terms.
