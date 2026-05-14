from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.csrf import csrf_protect
from django.utils import timezone
from django.db.models import Q
import uuid
from core.permissions import admin_required
from .models import MembershipApplication, User
from .forms.membership_forms import MembershipApplicationForm
from core.security import rate_limit


# ─── Public Membership Application (No Login Required) ─────────

@csrf_protect
@rate_limit(max_requests=5, window=300)
def membership_apply(request):
    if request.method == 'POST':
        form = MembershipApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                application.ip_address = x_forwarded_for.split(',')[0].strip()
            else:
                application.ip_address = request.META.get('REMOTE_ADDR')
            application.save()
            messages.success(
                request,
                'Your membership application has been submitted! We will review it and contact you.'
            )
            return redirect('users:membership_thanks')
    else:
        form = MembershipApplicationForm()

    return render(request, 'users/membership_apply.html', {
        'form': form,
        'title': 'Apply for Membership',
    })


def membership_thanks(request):
    return render(request, 'users/membership_thanks.html')


# ─── Admin Review (Admin Only) ─────────────────────────────────

@admin_required
def membership_list(request):
    applications = MembershipApplication.objects.all()
    pending_count = applications.filter(status='pending').count()
    return render(request, 'users/membership_list.html', {
        'applications': applications,
        'pending_count': pending_count,
    })


@admin_required
def membership_review(request, pk):
    application = get_object_or_404(MembershipApplication, pk=pk)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        admin_notes = request.POST.get('admin_notes', '')

        if new_status in ['approved', 'rejected', 'interview']:
            if new_status == 'approved':
                email_verified = request.POST.get('email_verified')
                if not email_verified:
                    messages.error(
                        request,
                        'You must verify the applicant email address before approval.'
                    )
                    return render(request, 'users/membership_review.html', {
                        'application': application,
                    })

            application.status = new_status
            application.admin_notes = admin_notes
            application.reviewed_by = request.user
            application.reviewed_at = timezone.now()

            if new_status == 'approved':
                if not application.signup_token:
                    application.signup_token = uuid.uuid4()
                    application.signup_token_created_at = timezone.now()
                    application.signup_token_used = False

            application.save()

            if new_status == 'approved':
                messages.success(
                    request,
                    'Application approved! Signup link generated. Copy it from the panel below.'
                )
            else:
                messages.success(request, f'Application marked as {new_status}.')

            return redirect('users:membership_list')

    return render(request, 'users/membership_review.html', {
        'application': application,
    })


# ─── Account Creation from Approved Application ────────────────

def membership_signup(request, token):
    """
    Allows an approved applicant to create their account.
    Token is validated, and account is created with Staff role.
    """
    application = get_object_or_404(
        MembershipApplication,
        signup_token=token,
        status='approved',
        signup_token_used=False
    )

    if application.signup_token_created_at:
        expiry_time = application.signup_token_created_at + timezone.timedelta(hours=72)
        if timezone.now() > expiry_time:
            messages.error(
                request,
                'This signup link has expired. Please contact the association for a new one.'
            )
            return redirect('core:landing')

    if request.method == 'POST':
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        errors = []
        if not password1 or not password2:
            errors.append('Please fill in both password fields.')
        elif password1 != password2:
            errors.append('Passwords do not match.')
        elif len(password1) < 8:
            errors.append('Password must be at least 8 characters long.')

        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            if User.objects.filter(email=application.email).exists():
                messages.error(
                    request,
                    '⚠️ An account with this email address already exists. '
                    'If you believe this is an error, please contact the association immediately.'
                )
                return render(request, 'users/membership_signup.html', {
                    'application': application,
                    'token': token,
                })

            user = User.objects.create_user(
                username=application.email,
                email=application.email,
                first_name=application.first_name,
                last_name=application.last_name,
                password=password1,
                role='staff',
                is_active=True
            )

            application.signup_token_used = True
            application.account_created = True
            application.save()

            login(request, user)
            messages.success(
                request,
                'Your account has been created! Welcome to the Association for Mercy.'
            )
            return redirect('core:dashboard')

    return render(request, 'users/membership_signup.html', {
        'application': application,
        'token': token,
    })


# ─── User Management (Super Admin Only) ────────────────────────

def is_super_admin(user):
    return user.is_authenticated and user.is_super_admin


@login_required
@user_passes_test(is_super_admin)
def user_management(request):
    """Super Admin view: manage all users."""
    users = User.objects.all().order_by('-date_joined')
    query = request.GET.get('q', '')
    role_filter = request.GET.get('role', '')
    status_filter = request.GET.get('status', '')

    if query:
        users = users.filter(
            Q(email__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )
    if role_filter:
        users = users.filter(role=role_filter)
    if status_filter:
        if status_filter == 'active':
            users = users.filter(is_active=True)
        elif status_filter == 'disabled':
            users = users.filter(is_active=False)

    super_admin_count = User.objects.filter(role='super_admin', is_active=True).count()

    return render(request, 'users/user_management.html', {
        'users': users,
        'query': query,
        'role_filter': role_filter,
        'status_filter': status_filter,
        'super_admin_count': super_admin_count,
    })


@login_required
@user_passes_test(is_super_admin)
def user_toggle_active(request, pk):
    """Super Admin view: activate or deactivate a user."""
    if request.method != 'POST':
        return redirect('users:user_management')

    target_user = get_object_or_404(User, pk=pk)

    # Prevent deactivating yourself
    if target_user == request.user:
        messages.error(request, 'You cannot deactivate your own account.')
        return redirect('users:user_management')

    # Prevent deactivating the last super admin
    if target_user.role == 'super_admin' and target_user.is_active:
        active_super_admins = User.objects.filter(role='super_admin', is_active=True).count()
        if active_super_admins <= 1:
            messages.error(request, 'Cannot deactivate the last active Super Admin.')
            return redirect('users:user_management')

    target_user.is_active = not target_user.is_active
    target_user.save()

    action = 'activated' if target_user.is_active else 'deactivated'
    messages.success(request, f'User {target_user.email} has been {action}.')
    return redirect('users:user_management')


@login_required
@user_passes_test(is_super_admin)
def user_change_role(request, pk):
    """Super Admin view: promote or demote a user."""
    if request.method != 'POST':
        return redirect('users:user_management')

    target_user = get_object_or_404(User, pk=pk)
    new_role = request.POST.get('role')

    if new_role not in ['super_admin', 'admin', 'staff']:
        messages.error(request, 'Invalid role.')
        return redirect('users:user_management')

    # Prevent changing your own role
    if target_user == request.user:
        messages.error(request, 'You cannot change your own role.')
        return redirect('users:user_management')

    # Prevent demoting the last super admin
    if target_user.role == 'super_admin' and new_role != 'super_admin':
        active_super_admins = User.objects.filter(role='super_admin', is_active=True).count()
        if active_super_admins <= 1:
            messages.error(request, 'Cannot remove the last Super Admin.')
            return redirect('users:user_management')

    old_role = target_user.get_role_display()
    target_user.role = new_role
    target_user.save()

    messages.success(request, f'{target_user.email} changed from {old_role} to {target_user.get_role_display()}.')
    return redirect('users:user_management')

# ─── Membership Report (Admin) ────────────────────────────────
from datetime import datetime
from core.reports import generate_pdf_report, generate_excel_report, log_export

@admin_required
def membership_report(request):
    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    year_filter = request.GET.get('year', '')
    month_filter = request.GET.get('month', '')

    apps = MembershipApplication.objects.all()
    if query:
        apps = apps.filter(Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(email__icontains=query))
    if status_filter:
        apps = apps.filter(status=status_filter)
    if year_filter:
        apps = apps.filter(submitted_at__year=year_filter)
    if month_filter:
        apps = apps.filter(submitted_at__month=month_filter)
    apps = apps.order_by('-submitted_at')
    available_years = MembershipApplication.objects.dates('submitted_at', 'year').values_list('submitted_at__year', flat=True).distinct()

    if request.method == 'POST':
        export_type = request.POST.get('export_type')
        headers = ['Name', 'Email', 'Phone', 'Nationality', 'Occupation', 'Status', 'Submitted']
        data = [[a.full_name, a.email, a.phone, a.nationality or '—', a.occupation or '—', a.get_status_display(), a.submitted_at.strftime('%Y-%m-%d')] for a in apps]
        xff = request.META.get('HTTP_X_FORWARDED_FOR')
        ip = xff.split(',')[0].strip() if xff else request.META.get('REMOTE_ADDR')
        log_export(request.user, 'membership_applications', export_type, {'q': query, 'status': status_filter, 'year': year_filter, 'month': month_filter}, ip)
        if export_type == 'pdf':
            return generate_pdf_report('Membership Report', headers, data, f'memberships_{datetime.now().strftime("%Y%m%d_%H%M")}.pdf')
        elif export_type == 'excel':
            return generate_excel_report(headers, data, f'memberships_{datetime.now().strftime("%Y%m%d_%H%M")}.xlsx')

    return render(request, 'users/membership_report.html', {
        'applications': apps, 'query': query, 'status_filter': status_filter,
        'year_filter': year_filter, 'month_filter': month_filter, 'available_years': available_years,
    })
    

# ─── User Report (Super Admin) ─────────────────────────────────

@login_required
@user_passes_test(is_super_admin)
def user_report(request):
    query = request.GET.get('q', '')
    role_filter = request.GET.get('role', '')
    status_filter = request.GET.get('status', '')
    year_filter = request.GET.get('year', '')
    month_filter = request.GET.get('month', '')

    users = User.objects.all()
    if query:
        users = users.filter(Q(email__icontains=query) | Q(first_name__icontains=query) | Q(last_name__icontains=query))
    if role_filter:
        users = users.filter(role=role_filter)
    if status_filter == 'active':
        users = users.filter(is_active=True)
    elif status_filter == 'disabled':
        users = users.filter(is_active=False)
    if year_filter:
        users = users.filter(date_joined__year=year_filter)
    if month_filter:
        users = users.filter(date_joined__month=month_filter)
    users = users.order_by('-date_joined')
    available_years = User.objects.dates('date_joined', 'year').values_list('date_joined__year', flat=True).distinct()

    if request.method == 'POST':
        export_type = request.POST.get('export_type')
        headers = ['Name', 'Email', 'Role', 'Status', 'Joined']
        data = [[u.get_full_name(), u.email, u.get_role_display(), 'Active' if u.is_active else 'Disabled', u.date_joined.strftime('%Y-%m-%d')] for u in users]
        xff = request.META.get('HTTP_X_FORWARDED_FOR')
        ip = xff.split(',')[0].strip() if xff else request.META.get('REMOTE_ADDR')
        log_export(request.user, 'users', export_type, {'q': query, 'role': role_filter, 'status': status_filter, 'year': year_filter, 'month': month_filter}, ip)
        if export_type == 'pdf':
            return generate_pdf_report('User Report', headers, data, f'users_{datetime.now().strftime("%Y%m%d_%H%M")}.pdf')
        elif export_type == 'excel':
            return generate_excel_report(headers, data, f'users_{datetime.now().strftime("%Y%m%d_%H%M")}.xlsx')

    return render(request, 'users/user_report.html', {
        'users': users, 'query': query, 'role_filter': role_filter,
        'status_filter': status_filter, 'year_filter': year_filter,
        'month_filter': month_filter, 'available_years': available_years,
    })