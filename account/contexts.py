from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse


def modal_login_form(request):
    '''
    Context that provides a login form and next path for the login modal where required.
    '''
    add_context = {'login_form': None}
    if not request.user.is_authenticated and request.path != reverse('login'):
        add_context['login_form'] = AuthenticationForm()
        if not request.path.startswith('/account/'):  # Avoid account paths so user isn't redirected to 403 for signup page etc.
            add_context['login_next'] = request.path

    return add_context
