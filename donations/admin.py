from django.contrib import admin
from .models import Donation, DonationIntent


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ('receipt_number', 'donor_name', 'amount', 'currency', 'payment_method', 'donation_date')
    list_filter = ('payment_method', 'donation_date', 'currency')
    search_fields = ('donor_name', 'donor_email', 'receipt_number')
    readonly_fields = ('created_at', 'receipt_number', 'recorded_by')
    ordering = ('-donation_date',)

    fieldsets = (
        ('Donor Information', {
            'fields': ('donor_name', 'donor_email', 'donor_phone', 'is_anonymous')
        }),
        ('Donation Details', {
            'fields': ('amount', 'currency', 'payment_method', 'donation_date', 'program')
        }),
        ('Receipt', {
            'fields': ('receipt_number', 'notes')
        }),
        ('Audit', {
            'fields': ('recorded_by', 'created_at')
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:
            obj.recorded_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(DonationIntent)
class DonationIntentAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'donation_type', 'estimated_value', 'status', 'submitted_at')
    list_filter = ('status', 'donation_type', 'submitted_at')
    search_fields = ('full_name', 'email', 'description')
    readonly_fields = ('submitted_at', 'ip_address')

    fieldsets = (
        ('Submitter Information', {
            'fields': ('full_name', 'email', 'phone')
        }),
        ('Donation Intent', {
            'fields': ('donation_type', 'description', 'estimated_value')
        }),
        ('Review', {
            'fields': ('status', 'admin_notes', 'reviewed_by', 'reviewed_at')
        }),
        ('Security', {
            'fields': ('ip_address', 'submitted_at'),
            'classes': ('collapse',)
        }),
    )