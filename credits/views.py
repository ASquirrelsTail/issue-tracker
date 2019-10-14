from django.views.generic.base import TemplateView, View
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.conf import settings
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
import json
from credits.forms import GetCreditsForm
from credits.models import PaymentIntent, Credit
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
    Wallet view. Uses the existing wallet_amount context variable.
    '''
    template_name = 'wallet.html'


class GetCreditsView(HasWalletMixin, FormView):
    '''
    View for users to buy credits.
    '''
    template_name = 'get_credits.html'
    form_class = GetCreditsForm

    def form_valid(self, form):
        '''
        Once the user chooses an ammount, a payment intent is created, and the payment page with the Stripe.js API is returned.
        Overrides success url redirect.
        '''
        no_credits = form.cleaned_data['no_credits']
        charge = no_credits * 60
        intent = PaymentIntent.objects.create_payment_intent(user=self.request.user, credits=no_credits, amount=charge)
        intent.save()
        return render(self.request, 'get_credits_pay.html',
                      {'client_secret': intent.client_secret, 'stripe_publishable': settings.STRIPE_PUBLISHABLE,
                       'charge': '{:.2f}'.format(charge / 100), 'no_credits': no_credits, 'intent_db_id': intent.id})


class RefundView(HasWalletMixin, SingleObjectMixin, TemplateView, View):
    '''
    View to refund a users latest transaction, if they have at least that many credits remaining.
    '''
    template_name = 'refund.html'
    http_method_names = ['get', 'post']
    context_object_name = 'transaction'

    def get_object(self, queryset=None):
        '''
        Gets the most recent unrefunded transaction.
        '''
        try:
            self.object = self.request.user.wallet.credit_set.filter(refunded=False).order_by('-created')[0]
        except Credit.DoesNotExist:
            self.object = None

        return self.object

    def get_context_data(self, **kwargs):
        self.get_object()
        context = super(RefundView, self).get_context_data(**kwargs)
        context['refund_value'] = '{:.2f}'.format(self.object.real_value / 100)

    def post(self, request):
        if self.object and self.object.can_refund:
            success, amount = self.object.refund()
            if success:
                messages.success('Successfully refunded {:.2f}'.format(amount / 100))
            return redirect(reverse_lazy('wallet'))
        else:
            return self.get(request)


class CheckIntentView(LoginRequiredMixin, SingleObjectMixin, View):
    '''
    View to poll payment intents for completion.
    '''
    model = PaymentIntent
    http_method_names = ['get']

    def get(self, request, pk):
        intent = self.get_object()
        if intent.user != request.user:
            raise PermissionDenied()
        if intent.complete:
            messages.success(self.request, 'Payment successful.')
        response = {'success': intent.complete}
        return HttpResponse(json.dumps(response), content_type='application/json')


class StripeWebhookView(View):
    '''
    View to provide webhook for Stripe payment events.
    '''
    http_method_names = ['post']

    @method_decorator(csrf_exempt)  # View needs to be CSRF exmpt to allow Stripe to send POST requests.
    def dispatch(self, request, *args, **kwargs):
        return super(StripeWebhookView, self).dispatch(request, *args, **kwargs)

    def post(self, request):
        '''
        Checks validity of posted payment event json and deals with it as apropriate.
        '''
        payload = request.body

        try:
            event = stripe.Event.construct_from(json.loads(payload), stripe.api_key)
        except (ValueError, stripe.error.SignatureVerificationError):
            # Invalid payload or invalid signature
            return HttpResponse(status=400)

        event_dict = event.to_dict()

        if event_dict['type'] == "payment_intent.succeeded":
            # If the event is a successful payment, match it to a stored intent object, and fulfill the payment.
            intent = event_dict['data']['object']
            try:
                payment_intent = PaymentIntent.objects.get(intent_id=intent['id'])
                payment_intent.fulfill()
            except PaymentIntent.DoesNotExist:
                # If the payment intent doesn't exist in the system, something needs to be done by a human being...
                # Payment has been made, but the order cannot be fulfilled. Payment probably needs refunding.
                print('Payment succeded, but failed to find payment intent in tracker DB.')

        return HttpResponse(status=200)
