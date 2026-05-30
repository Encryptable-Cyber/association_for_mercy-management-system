from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from core.permissions import staff_required
from .models import Program
from datetime import datetime
from .forms.program_forms import ProgramForm
try:
    from core.reports import generate_pdf_report, generate_excel_report, log_export
except ImportError:
    generate_pdf_report = None
    generate_excel_report = None
    log_export = None


@staff_required
def program_list(request):
    """List all programs."""
    programs = Program.objects.all()
    return render(request, 'programs/program_list.html', {
        'programs': programs,
    })


@staff_required
def program_create(request):
    """Create a new program."""
    if request.method == 'POST':
        form = ProgramForm(request.POST)
        if form.is_valid():
            program = form.save(commit=False)
            program.created_by = request.user
            program.save()
            messages.success(request, f'Program "{program.name}" created successfully.')
            return redirect('programs:list')
    else:
        form = ProgramForm()

    return render(request, 'programs/program_form.html', {
        'form': form,
        'title': 'Create New Program',
        'action': 'Create'
    })


@staff_required
def program_detail(request, pk):
    """View program details."""
    program = get_object_or_404(Program, pk=pk)
    cases = program.cases.all()
    donations = program.donations.all()

    return render(request, 'programs/program_detail.html', {
        'program': program,
        'cases': cases,
        'donations': donations,
    })


@staff_required
def program_edit(request, pk):
    """Edit an existing program."""
    program = get_object_or_404(Program, pk=pk)

    if request.method == 'POST':
        form = ProgramForm(request.POST, instance=program)
        if form.is_valid():
            form.save()
            messages.success(request, f'Program "{program.name}" updated successfully.')
            return redirect('programs:detail', pk=program.pk)
    else:
        form = ProgramForm(instance=program)

    return render(request, 'programs/program_form.html', {
        'form': form,
        'title': f'Edit: {program.name}',
        'action': 'Update'
    })

# ─── Reporting Views ──────────────────────────────────────────

@staff_required
def program_report(request):
    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    year_filter = request.GET.get('year', '')
    month_filter = request.GET.get('month', '')

    programs = Program.objects.all()
    if query:
        programs = programs.filter(Q(name__icontains=query) | Q(description__icontains=query))
    if status_filter:
        programs = programs.filter(status=status_filter)
    if year_filter:
        programs = programs.filter(start_date__year=year_filter)
    if month_filter:
        programs = programs.filter(start_date__month=month_filter)
    programs = programs.order_by('-start_date')
    available_years = Program.objects.dates('start_date', 'year').values_list('start_date__year', flat=True).distinct()

    if request.method == 'POST':
        export_type = request.POST.get('export_type')
        headers = ['Name', 'Status', 'Start Date', 'End Date', 'Budget (XAF)', 'Created']
        data = [[p.name, p.get_status_display(), p.start_date.strftime('%Y-%m-%d'), p.end_date.strftime('%Y-%m-%d') if p.end_date else '—', str(p.budget), p.created_at.strftime('%Y-%m-%d')] for p in programs]
        xff = request.META.get('HTTP_X_FORWARDED_FOR')
        ip = xff.split(',')[0].strip() if xff else request.META.get('REMOTE_ADDR')
        log_export(request.user, 'programs', export_type, {'q': query, 'status': status_filter, 'year': year_filter, 'month': month_filter}, ip)
        if export_type == 'pdf':
            return generate_pdf_report('Program Report', headers, data, f'programs_{datetime.now().strftime("%Y%m%d_%H%M")}.pdf')
        elif export_type == 'excel':
            return generate_excel_report(headers, data, f'programs_{datetime.now().strftime("%Y%m%d_%H%M")}.xlsx')

    return render(request, 'programs/program_report.html', {
        'programs': programs, 'query': query, 'status_filter': status_filter,
        'year_filter': year_filter, 'month_filter': month_filter, 'available_years': available_years,
    })