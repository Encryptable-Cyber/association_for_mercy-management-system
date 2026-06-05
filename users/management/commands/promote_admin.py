"""
Management command: promote first staff/admin user to super_admin.
Run: python manage.py promote_admin
"""
from django.core.management.base import BaseCommand
from users.models import User


class Command(BaseCommand):
    help = 'Promote the first non-super_admin user to super_admin'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, help='Email of user to promote')

    def handle(self, *args, **options):
        email = options.get('email')

        if email:
            user = User.objects.filter(email=email).first()
        else:
            user = User.objects.exclude(role='super_admin').first()

        if user:
            user.role = 'super_admin'
            user.save()
            self.stdout.write(self.style.SUCCESS(
                f'✅ User "{user.email}" promoted to super_admin'
            ))
        else:
            self.stdout.write(self.style.WARNING('No eligible user found.'))
