from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from datetime import datetime
from core.permissions import staff_required
try:
    from core.reports import generate_pdf_report, generate_excel_report, log_export
except ImportError:
    # ReportLab/Openpyxl not installed — reports will be disabled
    generate_pdf_report = None
    generate_excel_report = None
    log_export = None
from .models import Beneficiary, Case, Intervention
from .forms.beneficiary_forms import BeneficiaryForm, CaseForm, InterventionForm


@staff_required
def beneficiary_list(request):
    """List all beneficiaries with search and filter."""
    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')

    beneficiaries = Beneficiary.objects.all()

    if query:
        beneficiaries = beneficiaries.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(phone__icontains=query)
        )

    if status_filter:
        beneficiaries = beneficiaries.filter(status=status_filter)

    context = {
        'beneficiaries': beneficiaries.order_by('-created_at'),
        'query': query,
        'status_filter': status_filter,
    }
    return render(request, 'beneficiaries/beneficiary_list.html', context)


@staff_required
def beneficiary_create(request):
    """Create a new beneficiary."""
    if request.method == 'POST':
        form = BeneficiaryForm(request.POST)
        if form.is_valid():
            beneficiary = form.save(commit=False)
            beneficiary.created_by = request.user
            beneficiary.save()
            messages.success(request, f'Beneficiary {beneficiary.full_name} created successfully.')
            return redirect('beneficiaries:list')
    else:
        form = BeneficiaryForm()

    return render(request, 'beneficiaries/beneficiary_form.html', {
        'form': form,
        'title': 'Add New Beneficiary',
        'action': 'Create'
    })


@staff_required
def beneficiary_detail(request, pk):
    """View beneficiary details including cases."""
    beneficiary = get_object_or_404(Beneficiary, pk=pk)
    cases = beneficiary.cases.all()

    return render(request, 'beneficiaries/beneficiary_detail.html', {
        'beneficiary': beneficiary,
        'cases': cases,
    })


@staff_required
def beneficiary_edit(request, pk):
    """Edit an existing beneficiary."""
    beneficiary = get_object_or_404(Beneficiary, pk=pk)

    if request.method == 'POST':
        form = BeneficiaryForm(request.POST, instance=beneficiary)
        if form.is_valid():
            form.save()
            messages.success(request, f'Beneficiary {beneficiary.full_name} updated successfully.')
            return redirect('beneficiaries:detail', pk=beneficiary.pk)
    else:
        form = BeneficiaryForm(instance=beneficiary)

    return render(request, 'beneficiaries/beneficiary_form.html', {
        'form': form,
        'title': f'Edit: {beneficiary.full_name}',
        'action': 'Update'
    })


@staff_required
def case_create(request, beneficiary_pk):
    """Create a case for a specific beneficiary."""
    beneficiary = get_object_or_404(Beneficiary, pk=beneficiary_pk)

    if request.method == 'POST':
        form = CaseForm(request.POST)
        if form.is_valid():
            case = form.save(commit=False)
            case.beneficiary = beneficiary
            case.created_by = request.user
            case.save()
            messages.success(request, f'Case created for {beneficiary.full_name}.')
            return redirect('beneficiaries:detail', pk=beneficiary.pk)
    else:
        form = CaseForm(initial={'beneficiary': beneficiary})

    return render(request, 'beneficiaries/case_form.html', {
        'form': form,
        'beneficiary': beneficiary,
        'title': f'New Case for {beneficiary.full_name}',
    })


@staff_required
def case_detail(request, pk):
    """View case details and interventions."""
    case = get_object_or_404(Case, pk=pk)
    interventions = case.interventions.all()

    return render(request, 'beneficiaries/case_detail.html', {
        'case': case,
        'interventions': interventions,
    })


@staff_required
def intervention_create(request, case_pk):
    """Add an intervention to a case."""
    case = get_object_or_404(Case, pk=case_pk)

    if request.method == 'POST':
        form = InterventionForm(request.POST)
        if form.is_valid():
            intervention = form.save(commit=False)
            intervention.case = case
            intervention.performed_by = request.user
            intervention.save()
            messages.success(request, 'Intervention recorded successfully.')
            return redirect('beneficiaries:case_detail', pk=case.pk)
    else:
        form = InterventionForm(initial={'case': case})

    return render(request, 'beneficiaries/intervention_form.html', {
        'form': form,
        'case': case,
        'title': f'Intervention for {case.title}',
    })


# ─── Reporting Views ──────────────────────────────────────────

@staff_required
def beneficiary_report(request):
    """Report view with enhanced filters: year, month, status, search."""
    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    year_filter = request.GET.get('year', '')
    month_filter = request.GET.get('month', '')

    beneficiaries = Beneficiary.objects.all()

    if query:
        beneficiaries = beneficiaries.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(phone__icontains=query)
        )
    if status_filter:
        beneficiaries = beneficiaries.filter(status=status_filter)
    if year_filter:
        beneficiaries = beneficiaries.filter(created_at__year=year_filter)
    if month_filter:
        beneficiaries = beneficiaries.filter(created_at__month=month_filter)

    beneficiaries = beneficiaries.order_by('-created_at')

    # Get available years for dropdown
    available_years = Beneficiary.objects.dates('created_at', 'year').values_list('created_at__year', flat=True).distinct()

    if request.method == 'POST':
        export_type = request.POST.get('export_type')
        filters = {'q': query, 'status': status_filter, 'year': year_filter, 'month': month_filter}

        headers = ['Name', 'Gender', 'Phone', 'Email', 'Status', 'Created']
        data = []
        for b in beneficiaries:
            data.append([
                b.full_name,
                b.get_gender_display(),
                b.phone or '—',
                b.email or '—',
                b.get_status_display(),
                b.created_at.strftime('%Y-%m-%d')
            ])

        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        ip = x_forwarded_for.split(',')[0].strip() if x_forwarded_for else request.META.get('REMOTE_ADDR')
        log_export(request.user, 'beneficiaries', export_type, filters, ip)

        if export_type == 'pdf':
            return generate_pdf_report(
                'Beneficiary Report',
                headers,
                data,
                f'beneficiaries_{datetime.now().strftime("%Y%m%d_%H%M")}.pdf'
            )
        elif export_type == 'excel':
            return generate_excel_report(
                headers,
                data,
                f'beneficiaries_{datetime.now().strftime("%Y%m%d_%H%M")}.xlsx'
            )

    return render(request, 'beneficiaries/beneficiary_report.html', {
        'beneficiaries': beneficiaries,
        'query': query,
        'status_filter': status_filter,
        'year_filter': year_filter,
        'month_filter': month_filter,
        'available_years': available_years,
    })