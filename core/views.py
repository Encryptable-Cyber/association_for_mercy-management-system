from django.shortcuts import render, redirect
from django.db.models import Sum
from django.core.cache import cache
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
    Stats are cached for 5 minutes to reduce database load.
    """
    if request.user.is_authenticated:
        return redirect('core:dashboard')

    # Try to get cached stats
    context = cache.get('landing_stats')
    if context is None:
        context = {
            'total_beneficiaries': Beneficiary.objects.count(),
            'active_programs': Program.objects.filter(status='active').count(),
            'donation_count': Donation.objects.count(),
            'open_cases': Case.objects.filter(status__in=['open', 'in_progress']).count(),
            'activities': Activity.objects.filter(is_active=True)
                          .select_related('created_by')
                          .order_by('order', '-date')[:6],
        }
        cache.set('landing_stats', context, 300)  # 5 minutes

    return render(request, 'core/landing.html', context)


@staff_required
def dashboard(request):
    """
    Main dashboard view - displays overview statistics.
    Requires authentication and staff role.
    Uses select_related() to avoid N+1 queries.
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
        'recent_beneficiaries': Beneficiary.objects.select_related('created_by')
                                  .order_by('-created_at')[:5],
        'recent_donations': Donation.objects.select_related('program', 'recorded_by')
                              .order_by('-donation_date')[:5],
        'recent_cases': Case.objects.select_related('beneficiary', 'program')
                         .filter(status__in=['open', 'in_progress'])
                         .order_by('-created_at')[:5],
    }
    return render(request, 'core/dashboard.html', context)