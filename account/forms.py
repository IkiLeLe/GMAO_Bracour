from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth import authenticate
from .models import CustomUser

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Your username',
        'class': 'form-control'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Your password',
        'class': 'form-control'
    }))

class SignupForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2', 'badge_number', 'first_name', 'last_name', 'position')

    username = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Your username',
        'class': 'form-control'
    }))
    email = forms.CharField(widget=forms.EmailInput(attrs={
        'placeholder': 'Your email address',
        'class': 'form-control'
    }))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Your password',
        'class': 'form-control'
    }))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Repeat password',
        'class': 'form-control'
    }))
    badge_number = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Your badge number',
        'class': 'form-control'
    }))
    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Your first name',
        'class': 'form-control'
    }))
    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Your last name',
        'class': 'form-control'
    }))
    position = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Your position',
        'class': 'form-control'
    }))

class EditProfileForm(UserChangeForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Your current password',
        'class': 'form-control'
    }))

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'username', 'position', 'email']

    def clean_password(self):
        password = self.cleaned_data.get('password')

        # Vérifier que le mot de passe actuel est correct
        user = authenticate(username=self.instance.username, password=password)
        if not user:
            raise forms.ValidationError('Incorrect current password.')

        return password
    
