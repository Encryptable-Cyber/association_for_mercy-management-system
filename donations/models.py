from django.db import models


class Donation(models.Model):
    """
    Tracks donations received by the NGO (manual entry).
    """
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('check', 'Check'),
        ('bank_transfer', 'Bank Transfer'),
        ('mobile_money', 'Mobile Money'),
        ('other', 'Other'),
    ]

    donor_name = models.CharField(max_length=200)
    donor_email = models.EmailField(blank=True)
    donor_phone = models.CharField(max_length=20, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='XAF')
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES
    )
    donation_date = models.DateField()
    program = models.ForeignKey(
        'programs.Program',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='donations'
    )
    is_anonymous = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    receipt_number = models.CharField(max_length=50, blank=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    recorded_by = models.ForeignKey(
        'users.User',
        on_delete=models.PROTECT,
        related_name='donations_recorded'
    )

    class Meta:
        ordering = ['-donation_date']
        indexes = [
            models.Index(fields=['donation_date']),
            models.Index(fields=['payment_method']),
        ]

    def __str__(self):
        return f"{self.donor_name} - {self.amount} {self.currency}"

    def save(self, *args, **kwargs):
        """Auto-generate receipt number if not provided."""
        if not self.receipt_number:
            last = Donation.objects.order_by('-id').first()
            next_id = (last.id + 1) if last else 1
            self.receipt_number = f"RCP-{next_id:06d}"
        super().save(*args, **kwargs)
        
        

class DonationIntent(models.Model):
    """
    Public donation request form - requires admin review.
    Submitted by external users who wish to donate.
    """
    DONATION_TYPE_CHOICES = [
        ('money', 'Financial Donation'),
        ('goods', 'Goods / In-Kind'),
        ('service', 'Service / Volunteering'),
    ]

    CURRENCY_CHOICES = [
        ('XAF', 'XAF - Central African CFA Franc'),
        ('XOF', 'XOF - West African CFA Franc'),
        ('USD', 'USD - US Dollar'),
        ('EUR', 'EUR - Euro'),
        ('GBP', 'GBP - British Pound'),
        ('CAD', 'CAD - Canadian Dollar'),
        ('NGN', 'NGN - Nigerian Naira'),
        ('GHC', 'GHS - Ghanaian Cedi'),
        ('KES', 'KES - Kenyan Shilling'),
        ('ZAR', 'ZAR - South African Rand'),
        ('OTHER', 'Other'),
    ]

    FREQUENCY_CHOICES = [
        ('one_time', 'One-time'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('annually', 'Annually'),
    ]

    CONTACT_METHOD_CHOICES = [
        ('email', 'Email'),
        ('phone', 'Phone'),
        ('either', 'Either'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('contacted', 'Contacted'),
    ]

    # Submitter information
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    nationality = models.CharField(max_length=100, blank=True, help_text='Your country of citizenship')
    country_of_residence = models.CharField(max_length=100, blank=True, help_text='Country where you currently live')
    donation_type = models.CharField(max_length=10, choices=DONATION_TYPE_CHOICES)
    currency = models.CharField(max_length=5, choices=CURRENCY_CHOICES, default='XAF')
    description = models.TextField(
        help_text='Describe what you would like to donate'
    )
    estimated_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        help_text='Optional: estimated value of donation'
    )
    frequency = models.CharField(
        max_length=10,
        choices=FREQUENCY_CHOICES,
        default='one_time'
    )
    preferred_contact = models.CharField(
        max_length=10,
        choices=CONTACT_METHOD_CHOICES,
        default='either',
        help_text='How would you like us to contact you?'
    )
    additional_notes = models.TextField(
        blank=True,
        help_text='Any additional information you would like to share'
    )

    # Review fields
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )
    admin_notes = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='donation_intents_reviewed'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)

    # Metadata
    submitted_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True,
        help_text='Recorded for security and audit purposes'
    )

    class Meta:
        ordering = ['-submitted_at']
        verbose_name = 'Donation Intent'
        verbose_name_plural = 'Donation Intents'

    def __str__(self):
        return f"{self.full_name} - {self.get_donation_type_display()}"