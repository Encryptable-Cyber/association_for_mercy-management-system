from django.db import models


class Program(models.Model):
    """
    Represents an NGO program or initiative.
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('planned', 'Planned'),
        ('cancelled', 'Cancelled'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    budget = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='planned'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.PROTECT,
        related_name='programs_created'
    )

    class Meta:
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return self.name