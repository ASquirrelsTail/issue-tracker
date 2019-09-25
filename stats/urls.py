from django.conf.urls import url
from stats.views import TicketStatsView

urlpatterns = [
    url(r'^(?P<pk>[0-9]+)/$', TicketStatsView.as_view(), name='ticket_stats'),
]
