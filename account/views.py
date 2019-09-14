from django.shortcuts import render, redirect
from django.views import View
from account.forms import UserSignUpForm
from django.contrib import auth
from issue_tracker.settings import LOGIN_REDIRECT_URL
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.contrib import messages

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
    def form_valid(self, form):
        messages.success(self.request, 'Successfully logged in.')
        return super(LogIn, self).form_valid(form)


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
                messages.success(request, 'Successfully created user {}'.format(user.username))
                return redirect(LOGIN_REDIRECT_URL)

        return self.get(request, signup_form)
