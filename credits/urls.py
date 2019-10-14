from django.conf.urls import url
from credits.views import WalletView, GetCreditsView, StripeWebhookView, CheckIntentView, RefundView


urlpatterns = [
    url(r'^$', WalletView.as_view(), name='wallet'),
    url(r'^get/$', GetCreditsView.as_view(), name='get_credits'),
    url(r'^refund/$', RefundView.as_view(), name='refund_credits'),
    url(r'^webhook/$', StripeWebhookView.as_view(), name='stripe_webhook'),
    url(r'^payment-success/(?P<pk>[0-9]+)/$', CheckIntentView.as_view(), name='check_intent'),
]
