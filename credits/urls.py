from django.conf.urls import url
from credits.views import WalletView, GetCreditsView, StripeWebhookView


urlpatterns = [
    url(r'^$', WalletView.as_view(), name='wallet'),
    url(r'^get/$', GetCreditsView.as_view(), name='get_credits'),
    url(r'^webhook/$', StripeWebhookView.as_view(), name='stripe_webhook'),
]
