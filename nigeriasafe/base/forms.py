from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Patient


class CustomUserCreationForm(UserCreationForm):
    full_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'placeholder': 'Your full name'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'Enter your email'}))

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('email',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'password1' in self.fields:
            self.fields['password1'].widget.attrs.update({'placeholder': 'Create a password'})
        if 'password2' in self.fields:
            self.fields['password2'].widget.attrs.update({'placeholder': 'Confirm password'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        names = self.cleaned_data['full_name'].split(' ', 1)
        user.first_name = names[0]
        if len(names) > 1:
            user.last_name = names[1]
        if commit:
            user.save()
        return user

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        exclude = ['user', 'created_at', 'updated_at', 'full_name']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'weight': forms.NumberInput(attrs={'placeholder': 'in Kg'}),
            'height': forms.NumberInput(attrs={'placeholder': 'in cm'}),
            'medical_conditions': forms.TextInput(attrs={'placeholder': 'e.g., Asthma, Diabetes, Hypertension...'}),
            'allergies': forms.TextInput(attrs={'placeholder': 'e.g., Penicillin, Peanuts, Bee stings...'}),
            'medications': forms.TextInput(attrs={'placeholder': 'e.g., insulin, ventolin inhaler...'}),
            'phone_number': forms.TextInput(attrs={'placeholder': 'e.g., +2348012345678'}),
            'emergency_contact_name': forms.TextInput(attrs={'placeholder': "Emergency contact's name"}),
            'emergency_contact_phone': forms.TextInput(attrs={'placeholder': "Emergency contact's phone"}),
            'emergency_contact_relationship': forms.TextInput(attrs={'placeholder': 'e.g., Spouse, Parent, Sibling'}),
        }
