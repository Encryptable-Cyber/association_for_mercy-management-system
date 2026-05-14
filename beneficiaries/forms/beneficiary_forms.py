from django import forms
from ..models import Beneficiary, Case, Intervention


class BeneficiaryForm(forms.ModelForm):
    """
    Secure form for creating and editing beneficiaries.
    All fields are validated through Django's ModelForm validation.
    """
    class Meta:
        model = Beneficiary
        fields = [
            'first_name', 'last_name', 'date_of_birth', 'gender',
            'phone', 'email', 'address', 'status', 'notes'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter first name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter last name'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., +237 6XX XXX XXX'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@example.com'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Enter address'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional notes...'
            }),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_phone(self):
        """Sanitize and validate phone number."""
        phone = self.cleaned_data.get('phone', '')
        # Remove any potentially dangerous characters
        phone = ''.join(c for c in phone if c.isdigit() or c in '+ -()')
        if phone and len(phone.replace('+', '').replace(' ', '').replace('-', '').replace('(', '').replace(')', '')) < 7:
            raise forms.ValidationError('Phone number seems too short.')
        return phone

    def clean_email(self):
        """Ensure email is lowercase for consistency."""
        email = self.cleaned_data.get('email', '')
        return email.lower().strip() if email else email


class CaseForm(forms.ModelForm):
    """Secure form for case creation and editing."""
    class Meta:
        model = Case
        fields = ['beneficiary', 'title', 'description', 'priority', 'status', 'program']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Case title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe the case...'
            }),
            'beneficiary': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'program': forms.Select(attrs={'class': 'form-select'}),
        }


class InterventionForm(forms.ModelForm):
    """Form for recording interventions on cases."""
    class Meta:
        model = Intervention
        fields = ['case', 'description']
        widgets = {
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe the intervention...'
            }),
            'case': forms.Select(attrs={'class': 'form-select'}),
        }