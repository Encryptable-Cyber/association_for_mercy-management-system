from django.db import models


class Activity(models.Model):
    """
    Represents an activity or event that can be displayed on the landing page.
    Managed by admin users.
    """
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image = models.ImageField(
        upload_to='activities/',
        blank=True,
        help_text='Upload an image for this activity (recommended: 800x600px)'
    )
    date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(
        default=True,
        help_text='Only active activities appear on the landing page'
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text='Lower numbers appear first'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.PROTECT,
        related_name='activities_created'
    )

    class Meta:
        verbose_name_plural = 'Activities'
        ordering = ['order', '-date', '-created_at']

    def __str__(self):
        return self.title
    
class ExportLog(models.Model):
    """
    Audit log for tracking data exports.
    Records who exported what and when.
    """
    EXPORT_TYPES = [
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('print', 'Print'),
    ]

    REPORT_TYPES = [
        ('beneficiaries', 'Beneficiaries'),
        ('donations', 'Donations'),
        ('donation_intents', 'Donation Intents'),
        ('programs', 'Programs'),
        ('membership_applications', 'Membership Applications'),
        ('users', 'Users'),
    ]

    user = models.ForeignKey(
        'users.User',
        on_delete=models.PROTECT,
        related_name='exports'
    )
    report_type = models.CharField(max_length=30, choices=REPORT_TYPES)
    export_type = models.CharField(max_length=10, choices=EXPORT_TYPES)
    filters_applied = models.TextField(blank=True, help_text='JSON string of filters used')
    exported_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)

    class Meta:
        verbose_name = 'Export Log'
        verbose_name_plural = 'Export Logs'
        ordering = ['-exported_at']

    def __str__(self):
        return f"{self.user.email} exported {self.get_report_type_display()} as {self.get_export_type_display()} on {self.exported_at.strftime('%Y-%m-%d %H:%M')}"