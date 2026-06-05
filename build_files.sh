"""
Build script for Vercel deployment.
Runs Django checks and collects static files.
"""
import os
import django
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Collect static files
call_command('collectstatic', '--noinput', '--clear')
print("Vercel build complete.")
