from django import forms
from django.core.exceptions import ValidationError

# Sign-in form
class SignInForm(forms.Form):
    username = forms.CharField(min_length=3, max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput, min_length=6, required=True)

# Sign-up form
class SignUpForm(forms.Form):
    username = forms.CharField(min_length=3, max_length=150, required=True)
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, min_length=6, required=True)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        # Add logic to check if username already exists
        # Example: if User.objects.filter(username=username).exists():
        #     raise ValidationError('Username already taken.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Add logic to check if email already exists
        # Example: if User.objects.filter(email=email).exists():
        #     raise ValidationError('Email already registered.')
        return email