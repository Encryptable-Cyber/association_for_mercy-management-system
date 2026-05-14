from django.shortcuts import render, redirect
from django.db.models import Sum
from core.permissions import staff_required
from beneficiaries.models import Beneficiary, Case
from programs.models import Program
from donations.models import Donation, DonationIntent
from users.models import MembershipApplication
from .models import Activity


def landing(request):
    """
    Landing page for visitors.
    If user is already authenticated, redirect to dashboard.
    """
    if request.user.is_authenticated:
        return redirect('core:dashboard')

    # Build context for the landing page
    context = {
        'total_beneficiaries': Beneficiary.objects.count(),
        'active_programs': Program.objects.filter(status='active').count(),
        'donation_count': Donation.objects.count(),
        'open_cases': Case.objects.filter(status__in=['open', 'in_progress']).count(),
        'activities': Activity.objects.filter(is_active=True).order_by('order', '-date')[:6],
    }
    return render(request, 'core/landing.html', context)


@staff_required
def dashboard(request):
    """
    Main dashboard view - displays overview statistics.
    Requires authentication and staff role.
    """
    context = {
        'total_beneficiaries': Beneficiary.objects.count(),
        'active_beneficiaries': Beneficiary.objects.filter(status='active').count(),
        'total_programs': Program.objects.count(),
        'active_programs': Program.objects.filter(status='active').count(),
        'total_donations': Donation.objects.aggregate(Sum('amount'))['amount__sum'] or 0,
        'donation_count': Donation.objects.count(),
        'open_cases': Case.objects.filter(status__in=['open', 'in_progress']).count(),
        'urgent_cases': Case.objects.filter(priority='urgent', status__in=['open', 'in_progress']).count(),
        'pending_donation_intents': DonationIntent.objects.filter(status='pending').count(),
        'pending_membership_applications': MembershipApplication.objects.filter(status='pending').count(),
        'recent_beneficiaries': Beneficiary.objects.order_by('-created_at')[:5],
        'recent_donations': Donation.objects.order_by('-donation_date')[:5],
        'recent_cases': Case.objects.filter(status__in=['open', 'in_progress']).order_by('-created_at')[:5],
    }
    return render(request, 'core/dashboard.html', context)