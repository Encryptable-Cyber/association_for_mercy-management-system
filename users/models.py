from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """
    Custom User model with role-based access control.
    Uses email for login instead of username.
    """
    ROLE_CHOICES = [
        ('super_admin', 'Super Admin'),
        ('admin', 'Admin'),
        ('staff', 'Staff'),
    ]

    email = models.EmailField(unique=True, blank=False, null=False)
    role = models.CharField(
        max_length=15,
        choices=ROLE_CHOICES,
        default='staff',
        help_text='Designates the user\'s role in the system.'
    )
    
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True,
        help_text='Professional profile photo (JPG, JPEG, PNG only, max 2MB)'
    )

    # Use email as the unique identifier for authentication
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"

    @property
    def is_super_admin(self):
        """Check if user has super admin role."""
        return self.role == 'super_admin'

    @property
    def is_admin(self):
        """Check if user has admin role (includes super_admin for full access)."""
        return self.role in ['admin', 'super_admin']

    @property
    def is_staff_user(self):
        """Check if user has staff role."""
        return self.role == 'staff'


class MembershipApplication(models.Model):
    """
    Public membership application - requires admin review.
    Enhanced with detailed applicant profiling.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('interview', 'Interview Scheduled'),
    ]

    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('P', 'Prefer not to say'),
    ]

    EDUCATION_CHOICES = [
        ('none', 'No Formal Education'),
        ('primary', 'Primary School'),
        ('secondary', 'Secondary School'),
        ('high_school', 'High School'),
        ('bachelor', 'Bachelor\'s Degree'),
        ('master', 'Master\'s Degree'),
        ('doctorate', 'Doctorate'),
        ('other', 'Other'),
    ]

    EMPLOYMENT_CHOICES = [
        ('employed', 'Employed'),
        ('self_employed', 'Self-Employed'),
        ('unemployed', 'Unemployed'),
        ('student', 'Student'),
        ('retired', 'Retired'),
        ('volunteer', 'Full-time Volunteer'),
    ]

    # Personal Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='P')
    nationality = models.CharField(max_length=100, blank=True, help_text='Your country of citizenship')
    country_of_residence = models.CharField(max_length=100, blank=True, help_text='Country where you currently live')
    city = models.CharField(max_length=100, blank=True, help_text='City where you live')
    address = models.TextField()

    # Professional Information
    occupation = models.CharField(max_length=100, blank=True)
    employment_status = models.CharField(max_length=15, choices=EMPLOYMENT_CHOICES, default='employed')
    education_level = models.CharField(max_length=15, choices=EDUCATION_CHOICES, default='bachelor')
    professional_skills = models.TextField(
        blank=True,
        help_text='List your professional skills relevant to NGO work (e.g., project management, accounting, social work)'
    )

    # Languages
    languages_spoken = models.CharField(
        max_length=300,
        blank=True,
        help_text='List languages you speak (e.g., English, French, Swahili)'
    )

    # Motivation & Contribution
    motivation = models.TextField(
        help_text='Why do you want to join the Association for Mercy? What inspires you about our mission?'
    )
    contribution = models.TextField(
        blank=True,
        help_text='What skills, resources, or time can you contribute to the association?'
    )
    previous_volunteering = models.TextField(
        blank=True,
        help_text='Describe any previous volunteering or community service experience'
    )
    areas_of_interest = models.CharField(
        max_length=300,
        blank=True,
        help_text='Which areas interest you most? (e.g., Health, Education, Emergency Relief, Youth)'
    )
    availability = models.CharField(
        max_length=100,
        blank=True,
        help_text='How much time can you commit? (e.g., 5 hours/week, weekends only)'
    )
    referral_source = models.CharField(
        max_length=200,
        blank=True,
        help_text='How did you hear about us?'
    )

    # Review fields
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='pending'
    )
    admin_notes = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='membership_applications_reviewed'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)

    # Account creation token (for approved applicants)
    signup_token = models.UUIDField(
        blank=True,
        null=True,
        unique=True,
        help_text='Unique token for account creation after approval'
    )
    signup_token_created_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text='When the signup token was generated'
    )
    signup_token_used = models.BooleanField(
        default=False,
        help_text='Whether the signup token has been used'
    )
    account_created = models.BooleanField(
        default=False,
        help_text='Whether the applicant has created their account'
    )

    # Metadata
    submitted_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True,
        help_text='Recorded for security and audit purposes'
    )

    class Meta:
        ordering = ['-submitted_at']
        verbose_name = 'Membership Application'
        verbose_name_plural = 'Membership Applications'

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.get_status_display()}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class MembershipDocument(models.Model):
    """
    Supporting document uploaded during membership application.
    Securely stored with randomized filenames.
    """
    application = models.ForeignKey(
        MembershipApplication,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    document = models.FileField(
        upload_to='membership_documents/%Y/%m/',
        help_text='Upload a supporting document (PDF, JPG, JPEG, PNG only)'
    )
    document_type = models.CharField(max_length=50, help_text='e.g., Birth Certificate, National ID, CV, Certificate')
    original_filename = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Membership Document'
        verbose_name_plural = 'Membership Documents'
        ordering = ['uploaded_at']

    def __str__(self):
        return f"{self.document_type} - {self.application.full_name}"
    

import secrets
import hashlib
from datetime import timedelta


class OTP(models.Model):
    """
    One-Time Password for email verification and login.
    OTP is hashed before storage for security.
    """
    PURPOSE_CHOICES = [
        ('account_activation', 'Account Activation'),
        ('login', 'Login Verification'),
        ('password_reset', 'Password Reset'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otps')
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES)
    otp_hash = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)
    attempts = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-created_at']

    @classmethod
    def generate_otp(cls, user, purpose):
        """Generate a 6-digit OTP, hash it, and save."""
        # Generate 6-digit OTP
        raw_otp = ''.join([str(secrets.randbelow(10)) for _ in range(6)])

        # Hash OTP before storage
        otp_hash = hashlib.sha256(raw_otp.encode()).hexdigest()

        # Create OTP record
        otp = cls.objects.create(
            user=user,
            purpose=purpose,
            otp_hash=otp_hash,
            expires_at=timezone.now() + timedelta(minutes=10)
        )

        return raw_otp  # Return raw OTP to send via email

    @classmethod
    def verify_otp(cls, user, raw_otp, purpose):
        """Verify an OTP. Returns True if valid, False otherwise."""
        otp_hash = hashlib.sha256(raw_otp.encode()).hexdigest()

        otp = cls.objects.filter(
            user=user,
            purpose=purpose,
            otp_hash=otp_hash,
            used=False,
            expires_at__gt=timezone.now()
        ).first()

        if otp:
            otp.used = True
            otp.save()
            return True

        # Increment attempts on failed tries
        cls.objects.filter(
            user=user,
            purpose=purpose,
            used=False,
            expires_at__gt=timezone.now()
        ).update(attempts=models.F('attempts') + 1)

        return False
    
class AuditLog(models.Model):
    """
    Immutable audit trail for sensitive membership actions.
    """
    ACTION_CHOICES = [
        ('application_submitted', 'Application Submitted'),
        ('application_under_review', 'Application Under Review'),
        ('application_approved', 'Application Approved'),
        ('application_rejected', 'Application Rejected'),
        ('document_uploaded', 'Document Uploaded'),
        ('invitation_sent', 'Invitation Sent'),
        ('account_created', 'Account Created'),
        ('otp_verified', 'OTP Verified'),
        ('otp_failed', 'OTP Failed'),
        ('password_reset_requested', 'Password Reset Requested'),
        ('password_reset_completed', 'Password Reset Completed'),
        ('role_changed', 'Role Changed'),
        ('account_deactivated', 'Account Deactivated'),
        ('account_reactivated', 'Account Reactivated'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_actions'
    )
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    description = models.TextField(blank=True)
    target_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_targets'
    )
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - {self.get_action_display()} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

def log_audit(user, action, description='', target_user=None, ip_address=None):
    """Helper to create audit log entries."""
    AuditLog.objects.create(
        user=user,
        action=action,
        description=description,
        target_user=target_user,
        ip_address=ip_address
    )