from django.contrib.auth.models import User
from django import forms
from django.contrib.auth.forms import UserCreationForm


class UserSignUpForm(UserCreationForm):
    '''
    Form for new user to sign up.
    '''

    email = forms.EmailField(help_text="Required. We will only use your email to help you retrieve your password.")

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
