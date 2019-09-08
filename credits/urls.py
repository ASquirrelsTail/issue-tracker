from django.conf.urls import url
from credits.views import WalletView, GetCreditsView


urlpatterns = [
    url(r'^$', WalletView.as_view(), name='wallet'),
    url(r'^get/$', GetCreditsView.as_view(), name='get_credits'),
]
