from django.shortcuts import render, redirect
from django.views import View
from account.forms import UserSignUpForm
from django.contrib import auth
from issue_tracker.settings import LOGIN_REDIRECT_URL

# Create your views here.


class SignUp(View):
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
                return redirect(LOGIN_REDIRECT_URL)
        else:
            return self.get(request, signup_form)
