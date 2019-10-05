from django.conf.urls import url
from tickets.views import (TicketsListView, TicketView, AddBugView, AddFeatureView, SetTicketStatusView, AddCommentView,
                           EditCommentView, EditTicketView, VoteForTicketView, DeleteTicketView, LabelListView,
                           AddLabelView, EditLabelView, DeleteLabelView)

urlpatterns = [
    url(r'^$', TicketsListView.as_view(), name='tickets-list'),
    url(r'^(?P<pk>[0-9]+)/$', TicketView.as_view(), name='ticket'),
    url(r'^(?P<pk>[0-9]+)/approved/$', SetTicketStatusView.as_view(status_field='approved'), name='approve-ticket'),
    url(r'^(?P<pk>[0-9]+)/doing/$', SetTicketStatusView.as_view(status_field='doing'), name='doing-ticket'),
    url(r'^(?P<pk>[0-9]+)/done/$', SetTicketStatusView.as_view(status_field='done'), name='done-ticket'),
    url(r'^report-bug/$', AddBugView.as_view(), name='add-bug'),
    url(r'^request-feature/$', AddFeatureView.as_view(), name='add-feature'),
    url(r'^(?P<pk>[0-9]+)/edit/$', EditTicketView.as_view(), name='edit-ticket'),
    url(r'^(?P<pk>[0-9]+)/delete/$', DeleteTicketView.as_view(), name='delete-ticket'),
    url(r'^(?P<pk>[0-9]+)/vote/$', VoteForTicketView.as_view(), name='vote-for-ticket'),
    url(r'^(?P<ticket_pk>[0-9]+)/comments/add/$', AddCommentView.as_view(), name='add-comment'),
    url(r'^(?P<ticket_pk>[0-9]+)/comments/(?P<comment_pk>[0-9]+)/reply/$', AddCommentView.as_view(), name='add-reply'),
    url(r'^(?P<ticket_pk>[0-9]+)/comments/(?P<pk>[0-9]+)/edit/$', EditCommentView.as_view(), name='edit-comment'),
    url(r'^labels/$', LabelListView.as_view(), name='labels'),
    url(r'^labels/add$', AddLabelView.as_view(), name='add-label'),
    url(r'^labels/(?P<pk>[0-9]+)/edit/$', EditLabelView.as_view(), name='edit-label'),
    url(r'^labels/(?P<pk>[0-9]+)/delete/$', DeleteLabelView.as_view(), name='delete-label'),
]
