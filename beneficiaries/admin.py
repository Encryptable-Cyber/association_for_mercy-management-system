from django.contrib import admin
from .models import Beneficiary, Case, Intervention


@admin.register(Beneficiary)
class BeneficiaryAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'gender', 'phone', 'status', 'created_at', 'created_by')
    list_filter = ('status', 'gender', 'created_at')
    search_fields = ('first_name', 'last_name', 'phone', 'email')
    readonly_fields = ('created_at', 'updated_at', 'created_by')
    ordering = ('-created_at',)

    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'date_of_birth', 'gender')
        }),
        ('Contact Details', {
            'fields': ('phone', 'email', 'address')
        }),
        ('Status & Notes', {
            'fields': ('status', 'notes')
        }),
        ('Audit', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # New record
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'beneficiary', 'priority', 'status', 'program', 'created_at')
    list_filter = ('status', 'priority', 'created_at')
    search_fields = ('title', 'description', 'beneficiary__first_name', 'beneficiary__last_name')
    readonly_fields = ('created_at', 'updated_at', 'created_by')
    autocomplete_fields = ('beneficiary', 'program')

    fieldsets = (
        ('Case Information', {
            'fields': ('title', 'description', 'beneficiary', 'program')
        }),
        ('Status', {
            'fields': ('priority', 'status')
        }),
        ('Audit', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Intervention)
class InterventionAdmin(admin.ModelAdmin):
    list_display = ('id', 'case', 'date', 'performed_by')
    list_filter = ('date', 'performed_by')
    search_fields = ('description', 'case__title')
    readonly_fields = ('date',)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.performed_by = request.user
        super().save_model(request, obj, form, change)