from django.views.generic.base import TemplateView, View
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from credits.forms import GetCreditsForm
from credits.models import Wallet


# Create your views here.


class HasWalletMixin(LoginRequiredMixin, UserPassesTestMixin):
    '''
    Ensures the user has a wallet to access (for instance members of the dev team don't want/need a wallet).
    As super users have all permissions by default this will automatically apply to them.
    '''
    raise_exception = True

    def test_func(self):
        return not self.request.user.has_perm('credits.cant_have_wallet')


class WalletView(HasWalletMixin, TemplateView):
    '''
    Wallet view.
    '''
    template_name = 'wallet.html'


class GetCreditsView(HasWalletMixin, FormView):
    template_name = 'get_credits.html'
    form_class = GetCreditsForm
    success_url = '/credits/'

    def form_valid(self, form):
        wallet = Wallet.objects.get_or_create(user=self.request.user)[0]
        print(form)
        wallet.credit(value=form.cleaned_data['no_credits'])
        return super(GetCreditsView, self).form_valid(form)


class CreatePaymentView(View):
    pass
