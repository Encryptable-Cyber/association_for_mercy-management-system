from django import forms
from django.core.validators import MinValueValidator
from ..models import Program


class ProgramForm(forms.ModelForm):
    """Secure form for program creation and editing."""
    class Meta:
        model = Program
        fields = ['name', 'description', 'start_date', 'end_date', 'budget', 'status']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Program name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe the program...'
            }),
            'start_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'end_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'budget': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'min': '0',
                'step': '0.01'
            }),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_budget(self):
        """Ensure budget is not negative."""
        budget = self.cleaned_data.get('budget')
        if budget is not None and budget < 0:
            raise forms.ValidationError('Budget cannot be negative.')
        return budget

    def clean(self):
        """Validate that end_date is after start_date."""
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and end_date < start_date:
            self.add_error('end_date', 'End date must be after start date.')
        return cleaned_data