from django import forms
from .models import bakery_models,register_model
from django.core.exceptions import ValidationError
import re


class bakery_forms(forms.ModelForm):
    class Meta:
        model = bakery_models
        fields = "__all__"
        widgets = {
            'Name':  forms.TextInput(attrs={'class': 'form-control'}),
            'Items': forms.TextInput(attrs={'class': 'form-control'}),
            'Price': forms.NumberInput(attrs={'class': 'form-control'}),
            'Stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'Image': forms.FileInput(attrs={'class': 'form-control'}),
        }


class register_forms(forms.Form):
    """
    Registration form with:
    - Username uniqueness check
    - Email uniqueness check
    - Password strength validation (min 8 chars, upper, lower, digit, special)
    - Confirm-password match
    """
    Username = forms.CharField(
        max_length=45,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
    )
    Email = forms.EmailField(
        max_length=60,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
    )
    Password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
        help_text='At least 8 characters, including uppercase, lowercase, digit, and special character.',
    )
    # Confirm_Password = forms.CharField(
    #     widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}),
    #     label='Confirm Password',
    # )

    def clean_Username(self):
        username = self.cleaned_data['Username'].strip()
        if register_model.objects.filter(Username__iexact=username).exists():
            raise ValidationError("This username is already taken.")
        return username

    def clean_Email(self):
        email = self.cleaned_data['Email'].strip().lower()
        if register_model.objects.filter(Email__iexact=email).exists():
            raise ValidationError("An account with this email already exists.")
        return email

    def clean_Password(self):
        password = self.cleaned_data.get('Password', '')
        errors = []
        if len(password) < 8:
            errors.append("at least 8 characters")
        if not re.search(r'[A-Z]', password):
            errors.append("an uppercase letter")
        if not re.search(r'[a-z]', password):
            errors.append("a lowercase letter")
        if not re.search(r'\d', password):
            errors.append("a digit")
        if not re.search(r'[^A-Za-z0-9]', password):
            errors.append("a special character")
        if errors:
            raise ValidationError(f"Password must contain: {', '.join(errors)}.")
        return password

    # def clean(self):
    #     cleaned_data = super().clean()
    #     password = cleaned_data.get('Password')
    #     confirm = cleaned_data.get('Confirm_Password')
    #     if password and confirm and password != confirm:
    #         self.add_error('Confirm_Password', "Passwords do not match.")
    #     return cleaned_data


class Login_form(forms.Form):
    username = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
    )


class ResetPasswordForm(forms.Form):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'New Password'
        })
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm Password'
        })
    )
