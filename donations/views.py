from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.db.models import Sum
from django.utils import timezone
from datetime import datetime
from core.permissions import staff_required, admin_required
from core.reports import generate_pdf_report, generate_excel_report, log_export
from .models import Donation, DonationIntent
from .forms.donation_forms import DonationForm, DonationIntentForm
from core.security import rate_limit
from programs.models import Program


# ─── Internal Donation Management (Staff + Admin) ──────────────

@staff_required
def donation_list(request):
    donations = Donation.objects.all()
    total = donations.aggregate(Sum('amount'))['amount__sum'] or 0
    return render(request, 'donations/donation_list.html', {
        'donations': donations,
        'total_donations': total,
    })


@staff_required
def donation_create(request):
    if request.method == 'POST':
        form = DonationForm(request.POST)
        if form.is_valid():
            donation = form.save(commit=False)
            donation.recorded_by = request.user
            donation.save()
            messages.success(request, f'Donation from {donation.donor_name} recorded successfully.')
            return redirect('donations:list')
    else:
        form = DonationForm()

    return render(request, 'donations/donation_form.html', {
        'form': form,
        'title': 'Record New Donation',
        'action': 'Record'
    })


# ─── Public Donation Intent (No Login Required) ────────────────

@csrf_protect
@rate_limit(max_requests=5, window=300)  # 5 requests per 5 minutes
def donation_intent_create(request):
    if request.method == 'POST':
        form = DonationIntentForm(request.POST)
        if form.is_valid():
            donation_intent = form.save(commit=False)
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                donation_intent.ip_address = x_forwarded_for.split(',')[0].strip()
            else:
                donation_intent.ip_address = request.META.get('REMOTE_ADDR')
            donation_intent.save()
            messages.success(
                request,
                'Thank you! Your donation intent has been submitted. We will contact you soon.'
            )
            return redirect('donations:intent_thanks')
    else:
        form = DonationIntentForm()

    return render(request, 'donations/donation_intent_form.html', {
        'form': form,
        'title': 'Donate to Association for Mercy',
    })


def donation_intent_thanks(request):
    return render(request, 'donations/donation_intent_thanks.html')


# ─── Admin Review (Admin Only) ─────────────────────────────────

@admin_required
def donation_intent_list(request):
    intents = DonationIntent.objects.all()
    pending_count = intents.filter(status='pending').count()
    return render(request, 'donations/donation_intent_list.html', {
        'intents': intents,
        'pending_count': pending_count,
    })


@admin_required
def donation_intent_review(request, pk):
    intent = get_object_or_404(DonationIntent, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        admin_notes = request.POST.get('admin_notes', '')
        if new_status in ['approved', 'rejected', 'contacted']:
            intent.status = new_status
            intent.admin_notes = admin_notes
            intent.reviewed_by = request.user
            intent.reviewed_at = timezone.now()
            intent.save()
            messages.success(request, f'Donation intent marked as {new_status}.')
            return redirect('donations:intent_list')

    return render(request, 'donations/donation_intent_review.html', {
        'intent': intent,
    })


# ─── Reporting Views ──────────────────────────────────────────

@staff_required
def donation_report(request):
    query = request.GET.get('q', '')
    method_filter = request.GET.get('method', '')
    year_filter = request.GET.get('year', '')
    month_filter = request.GET.get('month', '')
    program_filter = request.GET.get('program', '')

    donations = Donation.objects.select_related('program').all()

    if query:
        donations = donations.filter(
            Q(donor_name__icontains=query) |
            Q(donor_email__icontains=query) |
            Q(receipt_number__icontains=query)
        )
    if method_filter:
        donations = donations.filter(payment_method=method_filter)
    if year_filter:
        donations = donations.filter(donation_date__year=year_filter)
    if month_filter:
        donations = donations.filter(donation_date__month=month_filter)
    if program_filter:
        donations = donations.filter(program_id=program_filter)

    donations = donations.order_by('-donation_date')
    available_years = Donation.objects.dates('donation_date', 'year').values_list('donation_date__year', flat=True).distinct()
    programs = Program.objects.all()

    if request.method == 'POST':
        export_type = request.POST.get('export_type')
        headers = ['Receipt #', 'Donor', 'Amount', 'Currency', 'Method', 'Date', 'Program']
        data = [[d.receipt_number, d.donor_name, str(d.amount), d.currency, d.get_payment_method_display(), d.donation_date.strftime('%Y-%m-%d'), d.program.name if d.program else '—'] for d in donations]
        xff = request.META.get('HTTP_X_FORWARDED_FOR')
        ip = xff.split(',')[0].strip() if xff else request.META.get('REMOTE_ADDR')
        log_export(request.user, 'donations', export_type, {'q': query, 'method': method_filter, 'year': year_filter, 'month': month_filter, 'program': program_filter}, ip)
        if export_type == 'pdf':
            return generate_pdf_report('Donation Report', headers, data, f'donations_{datetime.now().strftime("%Y%m%d_%H%M")}.pdf')
        elif export_type == 'excel':
            return generate_excel_report(headers, data, f'donations_{datetime.now().strftime("%Y%m%d_%H%M")}.xlsx')

    return render(request, 'donations/donation_report.html', {
        'donations': donations, 'query': query, 'method_filter': method_filter,
        'year_filter': year_filter, 'month_filter': month_filter,
        'program_filter': program_filter, 'available_years': available_years, 'programs': programs,
    })


from django.db.models import Q