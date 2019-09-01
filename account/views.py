from django.shortcuts import render, redirect
from django.views import View
from account.forms import UserSignUpForm
from django.contrib import auth
from issue_tracker.settings import LOGIN_REDIRECT_URL
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.views import LoginView
from credits.models import Wallet

# Create your views here.


class NotLoggedInMixin(UserPassesTestMixin):
    '''
    Mixin to check if a user is logged in, and return a 403 Forbidden error if they are.
    '''
    raise_exception = True

    def test_func(self):
        return not self.request.user.is_authenticated


class LogIn(NotLoggedInMixin, LoginView):
    '''
    Log in view requiring the user not to be logged in.
    '''
    pass


class SignUp(NotLoggedInMixin, View):
    '''
    View to sign up new users
    '''
    def get(self, request, signup_form=UserSignUpForm()):
        return render(request, 'registration/sign_up.html', {'form': signup_form})

    def post(self, request):
        signup_form = UserSignUpForm(request.POST)

        if signup_form.is_valid():
            signup_form.save()
            user = auth.authenticate(username=request.POST['username'], password=request.POST['password2'])

            if user:
                auth.login(user=user, request=request)
                # Once the user is successfully created assign them a wallet.
                wallet = Wallet(user=user)
                wallet.save()
                return redirect(LOGIN_REDIRECT_URL)

        return self.get(request, signup_form)
