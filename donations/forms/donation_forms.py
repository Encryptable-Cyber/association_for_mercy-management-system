from django import forms
from django.core.validators import MinValueValidator
from ..models import Donation, DonationIntent
from core.countries import COUNTRY_CHOICES

# Empty choice for optional country fields
COUNTRY_CHOICES_WITH_EMPTY = [('', '— Select Country —')] + COUNTRY_CHOICES


class DonationForm(forms.ModelForm):
    """Secure form for recording donations (internal use)."""
    class Meta:
        model = Donation
        fields = [
            'donor_name', 'donor_email', 'donor_phone',
            'amount', 'currency', 'payment_method',
            'donation_date', 'program', 'is_anonymous', 'notes'
        ]
        widgets = {
            'donor_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Donor full name'
            }),
            'donor_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'donor@example.com'
            }),
            'donor_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone number'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'min': '0.01',
                'step': '0.01'
            }),
            'currency': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'XAF'
            }),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'donation_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'program': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Additional notes...'
            }),
        }

    def clean_amount(self):
        """Ensure donation amount is positive."""
        amount = self.cleaned_data.get('amount')
        if amount is not None and amount <= 0:
            raise forms.ValidationError('Donation amount must be greater than zero.')
        return amount


class DonationIntentForm(forms.ModelForm):
    """
    PUBLIC form for donation intent submissions.
    Enhanced with country flags, phone code selector, and multi-currency.
    """
    nationality = forms.ChoiceField(
        choices=COUNTRY_CHOICES_WITH_EMPTY,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select country-select',
            'data-flag': 'true',
        })
    )
    country_of_residence = forms.ChoiceField(
        choices=COUNTRY_CHOICES_WITH_EMPTY,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select country-select',
            'data-flag': 'true',
        })
    )

    class Meta:
        model = DonationIntent
        fields = [
            'full_name', 'email', 'phone', 'nationality',
            'country_of_residence', 'donation_type', 'currency',
            'description', 'estimated_value', 'frequency',
            'preferred_contact', 'additional_notes'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your full name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your@email.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone number (without country code)',
                'data-phone-field': 'true',
            }),
            'donation_type': forms.Select(attrs={'class': 'form-select'}),
            'currency': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe what you would like to donate...'
            }),
            'estimated_value': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Optional estimated value',
                'min': '0',
                'step': '0.01'
            }),
            'frequency': forms.Select(attrs={'class': 'form-select'}),
            'preferred_contact': forms.Select(attrs={'class': 'form-select'}),
            'additional_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Any additional information...'
            }),
        }

    def clean_email(self):
        """Normalize email to lowercase."""
        email = self.cleaned_data.get('email', '')
        return email.lower().strip()

    def clean_description(self):
        """Ensure description is meaningful."""
        description = self.cleaned_data.get('description', '')
        if len(description.strip()) < 10:
            raise forms.ValidationError('Please provide more detail about your donation (at least 10 characters).')
        return description.strip()