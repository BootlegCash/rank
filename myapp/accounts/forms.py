from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile

class RegistrationForm(UserCreationForm):

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

class StatsUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'beer', 'floco', 'rum', 'whiskey', 'vodka', 'tequila',
            'shotguns', 'snorkels', 'thrown_up'
        ]

class SendFriendRequestForm(forms.Form):
    username = forms.CharField(label="Friend's Username", max_length=150)