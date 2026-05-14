from django.contrib.auth.models import AbstractUser
from django.db import models


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
        ('pending', 'Pending Review'),
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