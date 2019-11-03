from django.conf.urls import url
from django.conf import settings
from django.views.generic import RedirectView
from credits.views import WalletView, GetCreditsView, StripeWebhookView, CheckIntentView, RefundView

# If Stripe API key exists use the default urls, otherwise redirect them to the home page.
if settings.STRIPE_SECRET:
    urlpatterns = [
        url(r'^$', WalletView.as_view(), name='wallet'),
        url(r'^get/$', GetCreditsView.as_view(), name='get_credits'),
        url(r'^refund/$', RefundView.as_view(), name='refund_credits'),
        url(r'^webhook/$', StripeWebhookView.as_view(), name='stripe_webhook'),
        url(r'^payment-success/(?P<pk>[0-9]+)/$', CheckIntentView.as_view(), name='check_intent'),
    ]
else:
    urlpatterns = [
        url(r'^$', RedirectView.as_view(url='/'), name='wallet'),
        url(r'^get/$', RedirectView.as_view(url='/'), name='get_credits'),
        url(r'^refund/$', RedirectView.as_view(url='/'), name='refund_credits'),
    ]
