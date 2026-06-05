"""
WSGI handler for Vercel serverless deployment.
Wraps the Django WSGI application for Vercel's runtime.
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = get_wsgi_application()
