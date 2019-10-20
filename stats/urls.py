from django.conf.urls import url
from stats.views import TicketStatsView, AllTicketStatsView, TransactionsStatsView

urlpatterns = [
    url(r'^$', AllTicketStatsView.as_view(), name='all_ticket_stats'),
    url(r'^(?P<pk>[0-9]+)/$', TicketStatsView.as_view(), name='ticket_stats'),
    url(r'^transactions/$', TransactionsStatsView.as_view(), name='transaction_stats'),
]
