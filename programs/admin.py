from django.contrib import admin
from .models import Program


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'start_date', 'end_date', 'budget', 'created_by')
    list_filter = ('status', 'start_date')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at', 'created_by')
    ordering = ('-start_date',)

    fieldsets = (
        ('Program Details', {
            'fields': ('name', 'description')
        }),
        ('Dates & Budget', {
            'fields': ('start_date', 'end_date', 'budget')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Audit', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)