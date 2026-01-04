from django import forms
from .models import bakery_models,register_model

class bakery_forms(forms.ModelForm):
    class Meta:
        model=bakery_models
        fields="__all__"
        widgets={
            'Name':forms.TextInput(attrs={'class':'form-control'}),
            'Items':forms.TextInput(attrs={'class':'form-control'}),
            'Price':forms.NumberInput(attrs={'class':'form-control'}),
            'Date':forms.DateTimeInput(attrs={'class':'form-control','type':'date'}),
            'Image':forms.FileInput(attrs={'class':'form-control'}),
            'Link':forms.URLInput(attrs={'class':'form-control'}),
            
        }

class register_forms(forms.ModelForm):
    class Meta:
        model=register_model
        fields="__all__"
        widgets={
            'Username':forms.TextInput(attrs={'class':'form-control'}),
            'Email':forms.EmailInput(attrs={'class':'form-control'}),
            'Password':forms.PasswordInput(attrs={'class':'form-control'}),
        }

class Login_form(forms.Form):
    username=forms.CharField(max_length=50,widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Username'}))
    password=forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Password'}))