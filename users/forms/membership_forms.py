from django import forms
from ..models import MembershipApplication
from core.countries import COUNTRY_CHOICES, AREA_OF_INTEREST_CHOICES

# Empty choice for optional country fields
COUNTRY_CHOICES_WITH_EMPTY = [('', '— Select Country —')] + COUNTRY_CHOICES


class MembershipApplicationForm(forms.ModelForm):
    """
    PUBLIC form for membership applications.
    Comprehensive profiling with country flags, phone codes, and multi-select interests.
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
    areas_of_interest = forms.MultipleChoiceField(
        choices=AREA_OF_INTEREST_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input interest-checkbox',
        })
    )

    class Meta:
        model = MembershipApplication
        fields = [
            'first_name', 'last_name', 'email', 'phone',
            'date_of_birth', 'gender', 'nationality',
            'country_of_residence', 'city', 'address',
            'occupation', 'employment_status', 'education_level',
            'professional_skills', 'languages_spoken',
            'motivation', 'contribution', 'previous_volunteering',
            'areas_of_interest', 'availability', 'referral_source'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last name'
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
            'date_of_birth': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Yaoundé, Douala'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Your full address'
            }),
            'occupation': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your current occupation'
            }),
            'employment_status': forms.Select(attrs={'class': 'form-select'}),
            'education_level': forms.Select(attrs={'class': 'form-select'}),
            'professional_skills': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'e.g., Project management, accounting, social work, IT skills'
            }),
            'languages_spoken': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., English, French, Swahili, Arabic'
            }),
            'motivation': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Why do you want to join the Association for Mercy? What inspires you?'
            }),
            'contribution': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'What skills, resources, or time can you bring to our association?'
            }),
            'previous_volunteering': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe any previous volunteering or community service'
            }),
            'availability': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 5 hours/week, weekends, evenings'
            }),
            'referral_source': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Social media, Friend, Event, Website'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate existing areas_of_interest as a list for the checkboxes
        if self.instance and self.instance.pk and self.instance.areas_of_interest:
            self.initial['areas_of_interest'] = [
                v.strip() for v in self.instance.areas_of_interest.split(',') if v.strip()
            ]

    def clean_areas_of_interest(self):
        """Join multiple selected areas into a comma-separated string."""
        interests = self.cleaned_data.get('areas_of_interest', [])
        return ', '.join(interests) if interests else ''

    def clean_email(self):
        """Normalize email to lowercase."""
        email = self.cleaned_data.get('email', '')
        return email.lower().strip()

    def clean_motivation(self):
        """Ensure motivation statement is meaningful."""
        motivation = self.cleaned_data.get('motivation', '')
        if len(motivation.strip()) < 20:
            raise forms.ValidationError(
                'Please tell us more about your motivation (at least 20 characters).'
            )
        return motivation.strip()
    

from django import forms
from django.core.validators import FileExtensionValidator
from ..models import MembershipDocument

ALLOWED_EXTENSIONS = ['pdf', 'jpg', 'jpeg', 'png']
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


class MembershipDocumentForm(forms.ModelForm):
    """Secure document upload form with file type and size validation."""
    class Meta:
        model = MembershipDocument
        fields = ['document', 'document_type']
        widgets = {
            'document_type': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Birth Certificate, National ID, CV'
            }),
            'document': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png'
            }),
        }

    def clean_document(self):
        """Validate file type and size."""
        document = self.cleaned_data.get('document')
        if document:
            # Check extension
            ext = document.name.split('.')[-1].lower()
            if ext not in ALLOWED_EXTENSIONS:
                raise forms.ValidationError(
                    f'File type not allowed. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'
                )
            # Check size
            if document.size > MAX_FILE_SIZE:
                raise forms.ValidationError(
                    f'File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB'
                )
        return document