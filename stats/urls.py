from django.conf.urls import url
from stats.views import TicketStatsView, AllTicketStatsView

urlpatterns = [
    url(r'^$', AllTicketStatsView.as_view(), name='all_ticket_stats'),
    url(r'^(?P<pk>[0-9]+)/$', TicketStatsView.as_view(), name='ticket_stats'),
]
