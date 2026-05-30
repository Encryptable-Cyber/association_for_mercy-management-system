from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import PasswordResetConfirmView
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_protect
from django.utils import timezone
from django.db.models import Q
from django.core.mail import send_mail
import uuid
from datetime import datetime
from core.permissions import admin_required
from core.security import rate_limit
from .models import MembershipApplication, User, OTP, AuditLog, log_audit
from .forms.membership_forms import MembershipApplicationForm, MembershipDocumentForm

try:
    from core.reports import generate_pdf_report, generate_excel_report, log_export
except ImportError:
    generate_pdf_report = None
    generate_excel_report = None
    log_export = None


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

            # Audit log
            log_audit(
                user=None,
                action='application_submitted',
                description=f'Membership application from {application.full_name} ({application.email})',
                ip_address=application.ip_address
            )

            messages.success(
                request,
                'Your membership application has been submitted! We will review it and contact you.'
            )
            return redirect('users:membership_upload_document', pk=application.pk)
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

        if new_status in ['approved', 'rejected', 'interview', 'under_review']:
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

            # Audit log
            log_audit(
                user=request.user,
                action=f'application_{new_status}',
                description=f'Application #{application.id} ({application.full_name}) marked as {new_status}. Notes: {admin_notes}',
                ip_address=request.META.get('REMOTE_ADDR')
            )

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
                    'An account with this email address already exists.'
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
                is_active=False
            )

            profile_picture = request.FILES.get('profile_picture')
            if profile_picture:
                allowed_types = ['image/jpeg', 'image/jpg', 'image/png']
                if profile_picture.content_type not in allowed_types:
                    messages.error(request, 'Profile picture must be JPG, JPEG, or PNG.')
                    user.delete()
                    return render(request, 'users/membership_signup.html', {
                        'application': application,
                        'token': token,
                    })
                if profile_picture.size > 2 * 1024 * 1024:
                    messages.error(request, 'Profile picture must be under 2MB.')
                    user.delete()
                    return render(request, 'users/membership_signup.html', {
                        'application': application,
                        'token': token,
                    })
                user.profile_picture = profile_picture
                user.save()

            application.signup_token_used = True
            application.account_created = True
            application.save()

            # Audit log
            log_audit(
                user=user,
                action='account_created',
                description=f'Account created via invitation for {user.email}',
                ip_address=request.META.get('REMOTE_ADDR')
            )

            raw_otp = OTP.generate_otp(user, 'account_activation')
            request.session['otp_user_id'] = user.id
            request.session['otp_purpose'] = 'account_activation'

            try:
                send_mail(
                    'Account Activation OTP - Association for Mercy',
                    f'Your OTP for account activation is: {raw_otp}\n\nThis OTP expires in 10 minutes.',
                    'noreply@mercy.org',
                    [user.email],
                    fail_silently=False,
                )
            except Exception:
                messages.warning(request, f'Email could not be sent. Your OTP is: {raw_otp}')

            messages.success(request, 'Account created! Please check your email for the OTP.')
            return redirect('users:otp_verify')

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
    if request.method != 'POST':
        return redirect('users:user_management')

    target_user = get_object_or_404(User, pk=pk)

    if target_user == request.user:
        messages.error(request, 'You cannot deactivate your own account.')
        return redirect('users:user_management')

    if target_user.role == 'super_admin' and target_user.is_active:
        active_super_admins = User.objects.filter(role='super_admin', is_active=True).count()
        if active_super_admins <= 1:
            messages.error(request, 'Cannot deactivate the last active Super Admin.')
            return redirect('users:user_management')

    target_user.is_active = not target_user.is_active
    target_user.save()

    action = 'activated' if target_user.is_active else 'deactivated'

    # Audit log
    log_audit(
        user=request.user,
        action='account_deactivated' if not target_user.is_active else 'account_reactivated',
        description=f'User {target_user.email} {action}',
        target_user=target_user,
        ip_address=request.META.get('REMOTE_ADDR')
    )

    messages.success(request, f'User {target_user.email} has been {action}.')
    return redirect('users:user_management')


@login_required
@user_passes_test(is_super_admin)
def user_change_role(request, pk):
    if request.method != 'POST':
        return redirect('users:user_management')

    target_user = get_object_or_404(User, pk=pk)
    new_role = request.POST.get('role')

    if new_role not in ['super_admin', 'admin', 'staff']:
        messages.error(request, 'Invalid role.')
        return redirect('users:user_management')

    if target_user == request.user:
        messages.error(request, 'You cannot change your own role.')
        return redirect('users:user_management')

    if target_user.role == 'super_admin' and new_role != 'super_admin':
        active_super_admins = User.objects.filter(role='super_admin', is_active=True).count()
        if active_super_admins <= 1:
            messages.error(request, 'Cannot remove the last Super Admin.')
            return redirect('users:user_management')

    old_role = target_user.get_role_display()
    target_user.role = new_role
    target_user.save()

    # Audit log
    log_audit(
        user=request.user,
        action='role_changed',
        description=f'{target_user.email} changed from {old_role} to {target_user.get_role_display()}',
        target_user=target_user,
        ip_address=request.META.get('REMOTE_ADDR')
    )

    messages.success(request, f'{target_user.email} changed from {old_role} to {target_user.get_role_display()}.')
    return redirect('users:user_management')


@login_required
@user_passes_test(is_super_admin)
def user_reset_password(request, pk):
    if request.method != 'POST':
        return redirect('users:user_management')

    target_user = get_object_or_404(User, pk=pk)
    token = default_token_generator.make_token(target_user)
    uid = urlsafe_base64_encode(force_bytes(target_user.pk))

    reset_url = request.build_absolute_uri(f'/auth/reset/{uid}/{token}/')

    request.session['reset_link'] = reset_url
    request.session['reset_user_email'] = target_user.email

    # Audit log
    log_audit(
        user=request.user,
        action='password_reset_requested',
        description=f'Password reset requested for {target_user.email}',
        target_user=target_user,
        ip_address=request.META.get('REMOTE_ADDR')
    )

    messages.success(request, f'Password reset link generated.')
    return redirect('users:user_management')


# ─── Membership Report (Admin) ────────────────────────────────

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

    if request.method == 'POST' and generate_pdf_report:
        export_type = request.POST.get('export_type')
        headers = ['Name', 'Email', 'Phone', 'Nationality', 'Occupation', 'Status', 'Submitted']
        data = [[a.full_name, a.email, a.phone, a.nationality or '—', a.occupation or '—', a.get_status_display(), a.submitted_at.strftime('%Y-%m-%d')] for a in apps]
        xff = request.META.get('HTTP_X_FORWARDED_FOR')
        ip = xff.split(',')[0].strip() if xff else request.META.get('REMOTE_ADDR')
        if log_export:
            log_export(request.user, 'membership_applications', export_type, {'q': query}, ip)
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

    if request.method == 'POST' and generate_pdf_report:
        export_type = request.POST.get('export_type')
        headers = ['Name', 'Email', 'Role', 'Status', 'Joined']
        data = [[u.get_full_name(), u.email, u.get_role_display(), 'Active' if u.is_active else 'Disabled', u.date_joined.strftime('%Y-%m-%d')] for u in users]
        xff = request.META.get('HTTP_X_FORWARDED_FOR')
        ip = xff.split(',')[0].strip() if xff else request.META.get('REMOTE_ADDR')
        if log_export:
            log_export(request.user, 'users', export_type, {'q': query}, ip)
        if export_type == 'pdf':
            return generate_pdf_report('User Report', headers, data, f'users_{datetime.now().strftime("%Y%m%d_%H%M")}.pdf')
        elif export_type == 'excel':
            return generate_excel_report(headers, data, f'users_{datetime.now().strftime("%Y%m%d_%H%M")}.xlsx')

    return render(request, 'users/user_report.html', {
        'users': users, 'query': query, 'role_filter': role_filter,
        'status_filter': status_filter, 'year_filter': year_filter,
        'month_filter': month_filter, 'available_years': available_years,
    })


# ─── Document Upload for Membership Applications ──────────────

@csrf_protect
def membership_upload_document(request, pk):
    application = get_object_or_404(MembershipApplication, pk=pk, status='pending')

    if request.method == 'POST':
        form = MembershipDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.application = application
            document.original_filename = request.FILES['document'].name
            document.save()

            # Audit log
            log_audit(
                user=None,
                action='document_uploaded',
                description=f'Document "{document.document_type}" uploaded for application #{application.id} ({application.full_name})',
                ip_address=request.META.get('REMOTE_ADDR')
            )

            messages.success(request, 'Document uploaded successfully!')
            return redirect('users:membership_upload_document', pk=application.pk)
    else:
        form = MembershipDocumentForm()

    documents = application.documents.all()

    return render(request, 'users/membership_upload_document.html', {
        'form': form,
        'application': application,
        'documents': documents,
    })


# ─── OTP Verification ─────────────────────────────────────────

def otp_verify(request):
    user_id = request.session.get('otp_user_id')
    purpose = request.session.get('otp_purpose', 'account_activation')

    if not user_id:
        messages.error(request, 'No verification in progress.')
        return redirect('core:landing')

    user = get_object_or_404(User, pk=user_id)

    if request.method == 'POST':
        otp_input = request.POST.get('otp', '').strip()

        if len(otp_input) != 6 or not otp_input.isdigit():
            messages.error(request, 'Please enter a valid 6-digit OTP.')
        else:
            if OTP.verify_otp(user, otp_input, purpose):
                # Audit log
                log_audit(
                    user=user,
                    action='otp_verified',
                    description=f'OTP verified for {purpose}',
                    ip_address=request.META.get('REMOTE_ADDR')
                )

                if purpose == 'account_activation':
                    user.is_active = True
                    user.save()
                    login(request, user)
                    request.session.pop('otp_user_id', None)
                    request.session.pop('otp_purpose', None)
                    messages.success(request, 'Your account is now active! Welcome!')
                    return redirect('core:dashboard')
                elif purpose == 'login':
                    login(request, user)
                    request.session.pop('otp_user_id', None)
                    request.session.pop('otp_purpose', None)
                    messages.success(request, 'Login successful!')
                    return redirect('core:dashboard')
            else:
                # Audit log for failed attempt
                log_audit(
                    user=user,
                    action='otp_failed',
                    description=f'Failed OTP attempt for {purpose}',
                    ip_address=request.META.get('REMOTE_ADDR')
                )
                messages.error(request, 'Invalid or expired OTP. Please try again.')

    return render(request, 'users/otp_verify.html', {
        'purpose': purpose,
        'email': user.email,
    })


# ─── OTP Password Reset ──────────────────────────────────────

class OTPPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'registration/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')

    def dispatch(self, *args, **kwargs):
        if self.request.session.get('otp_verified_password_reset'):
            data = self.request.session.get('password_reset_form_data', {})
            user = self.get_user(kwargs['uidb64'])
            if user and data.get('new_password1'):
                user.set_password(data['new_password1'])
                user.save()

                # Audit log
                log_audit(
                    user=user,
                    action='password_reset_completed',
                    description=f'Password reset completed for {user.email}',
                    ip_address=self.request.META.get('REMOTE_ADDR')
                )

                messages.success(self.request, 'Password changed successfully! You can now log in.')
                self.request.session.pop('otp_verified_password_reset', None)
                self.request.session.pop('otp_user_id', None)
                self.request.session.pop('password_reset_form_data', None)
                return redirect('password_reset_complete')
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        user = form.user
        self.request.session['password_reset_form_data'] = {
            'new_password1': form.cleaned_data['new_password1'],
            'new_password2': form.cleaned_data['new_password2'],
        }
        raw_otp = OTP.generate_otp(user, 'password_reset')
        try:
            send_mail(
                'Password Reset OTP - Association for Mercy',
                f'Your OTP for password reset is: {raw_otp}\n\nThis OTP expires in 10 minutes.',
                'noreply@mercy.org',
                [user.email],
                fail_silently=False,
            )
        except Exception:
            messages.warning(self.request, f'Email could not be sent. Your OTP is: {raw_otp}')

        self.request.session['otp_user_id'] = user.id
        self.request.session['otp_purpose'] = 'password_reset'
        return redirect('users:otp_verify_password_reset')


def otp_verify_password_reset(request):
    user_id = request.session.get('otp_user_id')

    if not user_id:
        messages.error(request, 'No password reset in progress.')
        return redirect('login')

    user = get_object_or_404(User, pk=user_id)

    if request.method == 'POST':
        otp_input = request.POST.get('otp', '').strip()

        if len(otp_input) != 6 or not otp_input.isdigit():
            messages.error(request, 'Please enter a valid 6-digit OTP.')
        else:
            if OTP.verify_otp(user, otp_input, 'password_reset'):
                request.session['otp_verified_password_reset'] = True
                messages.success(request, 'OTP verified! Completing password reset...')
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                return redirect('password_reset_confirm', uidb64=uid, token=token)
            else:
                messages.error(request, 'Invalid or expired OTP. Please try again.')

    return render(request, 'users/otp_verify_password_reset.html', {
        'email': user.email,
    })


# ─── Audit Log (Super Admin Only) ─────────────────────────────

@login_required
@user_passes_test(is_super_admin)
def audit_log(request):
    logs = AuditLog.objects.select_related('user', 'target_user').all()[:200]
    action_filter = request.GET.get('action', '')

    if action_filter:
        logs = logs.filter(action=action_filter)

    return render(request, 'users/audit_log.html', {
        'logs': logs,
        'action_filter': action_filter,
    })