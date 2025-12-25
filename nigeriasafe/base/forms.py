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
            'medical_conditions': forms.Textarea(attrs={'rows': 3}),
            'allergies': forms.Textarea(attrs={'rows': 2}),
            'medications': forms.Textarea(attrs={'rows': 2}),
        }
