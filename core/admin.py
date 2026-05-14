from django.contrib import admin
from .models import Activity


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'order', 'date', 'created_at')
    list_filter = ('is_active', 'date')
    search_fields = ('title', 'description')
    list_editable = ('is_active', 'order')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Activity Details', {
            'fields': ('title', 'description', 'image', 'date')
        }),
        ('Display Settings', {
            'fields': ('is_active', 'order')
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)