from django.contrib.auth.models import User
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError


class UserSignUpForm(UserCreationForm):
    '''
    Form for new user to sign up.
    '''

    email = forms.EmailField(help_text="Required. We will only use your email to help you retrieve your password.")

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email):
            raise ValidationError(u'A user with that email address already exists.')
        else:
            return email
