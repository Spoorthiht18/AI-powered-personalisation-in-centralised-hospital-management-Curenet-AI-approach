web: gunicorn curenet_ai.wsgi:application
worker: python manage.py runworker channels
release: python manage.py migrate
