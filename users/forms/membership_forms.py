from django import forms
from ..models import MembershipApplication


class MembershipApplicationForm(forms.ModelForm):
    """
    PUBLIC form for membership applications.
    Comprehensive profiling with validation.
    """
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
                'placeholder': 'Phone number with country code'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'nationality': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Cameroonian, Nigerian, French'
            }),
            'country_of_residence': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Cameroon, France, USA'
            }),
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
            'areas_of_interest': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Health, Education, Emergency Relief, Youth Empowerment'
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