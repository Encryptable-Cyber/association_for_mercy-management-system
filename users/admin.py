from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, MembershipApplication


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        'email',
        'first_name',
        'last_name',
        'role',
        'is_active',
        'date_joined',
    )
    list_filter = ('role', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    list_editable = ('role', 'is_active')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'username')}),
        ('Role Information', {'fields': ('role',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'username', 'password1', 'password2'),
        }),
        ('Role Information', {'fields': ('role',)}),
    )

    def save_model(self, request, obj, form, change):
        """Prevent the last super admin from being demoted or deactivated."""
        if change:
            old_obj = User.objects.get(pk=obj.pk)
            # Prevent demoting the last super admin
            if old_obj.role == 'super_admin' and obj.role != 'super_admin':
                if not User.objects.filter(role='super_admin', is_active=True).exclude(pk=obj.pk).exists():
                    from django.contrib import messages
                    messages.error(request, 'Cannot remove the last active Super Admin.')
                    return
            # Prevent deactivating the last super admin
            if old_obj.is_active and not obj.is_active:
                if old_obj.role == 'super_admin' and not User.objects.filter(role='super_admin', is_active=True).exclude(pk=obj.pk).exists():
                    from django.contrib import messages
                    messages.error(request, 'Cannot deactivate the last active Super Admin.')
                    return
        super().save_model(request, obj, form, change)


@admin.register(MembershipApplication)
class MembershipApplicationAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'occupation', 'status', 'submitted_at')
    list_filter = ('status', 'submitted_at')
    search_fields = ('first_name', 'last_name', 'email', 'motivation')
    readonly_fields = ('submitted_at', 'ip_address')

    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'date_of_birth')
        }),
        ('Additional Details', {
            'fields': ('address', 'occupation', 'availability')
        }),
        ('Motivation & Skills', {
            'fields': ('motivation', 'skills')
        }),
        ('Review', {
            'fields': ('status', 'admin_notes', 'reviewed_by', 'reviewed_at')
        }),
        ('Security', {
            'fields': ('ip_address', 'submitted_at'),
            'classes': ('collapse',)
        }),
    )