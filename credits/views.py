from django.views.generic.base import TemplateView, View
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json
from credits.forms import GetCreditsForm
from credits.models import Wallet, PaymentIntent
import stripe

stripe.api_key = settings.STRIPE_SECRET

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
        # wallet = Wallet.objects.get_or_create(user=self.request.user)[0]
        # wallet.credit(value=form.cleaned_data['no_credits'])
        # return super(GetCreditsView, self).form_valid(form)
        no_credits = form.cleaned_data['no_credits']
        charge = no_credits * 60
        intent = PaymentIntent.objects.create_payment_intent(user=self.request.user, credits=no_credits, amount=charge)
        intent.save()
        return render(self.request, 'get_credits_pay.html',
                      {'client_secret': intent.client_secret, 'stripe_publishable': settings.STRIPE_PUBLISHABLE,
                       'charge': '{:.2f}'.format(charge / 100), 'no_credits': no_credits})


class StripeWebhookView(View):
    http_method_names = ['post']

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(StripeWebhookView, self).dispatch(request, *args, **kwargs)

    def post(self, request):
        # endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
        payload = request.body
        # sig_header = request.headers.get('STRIPE_SIGNATURE')

        try:
            event = stripe.Event.construct_from(json.loads(payload), stripe.api_key)
        except ValueError:
            # invalid payload
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError:
            # invalid signature
            return HttpResponse(status=400)

        event_dict = event.to_dict()
        if event_dict['type'] == "payment_intent.succeeded":
            intent = event_dict['data']['object']
            try:
                payment_intent = PaymentIntent.objects.get(intent_id=intent['id'])
                payment_intent.fulfill()
            except PaymentIntent.DoesNotExist:
                print('Payment succeded, but failed to find payment intent in tracker DB.')
            # Fulfill the customer's purchase
        elif event_dict['type'] == "payment_intent.payment_failed":
            pass
            # Notify the customer that payment failed

        return HttpResponse(status=200)
