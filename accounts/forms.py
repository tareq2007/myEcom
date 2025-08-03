from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import Profile

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['first_name', 'email', 'username', 'password1', 'password2']
        labels = {
            'first_name': 'Name',
        }

class UserForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ['first_name', 'email', 'username']

class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = ['location', 'bio', 'short_intro', 'profile_image', 'social_github', 'social_linkedin', 'social_website']
