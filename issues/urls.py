from django.conf.urls import url
from issues.views import IssuesListView, IssueView

urlpatterns = [
    url(r'^$', IssuesListView.as_view(), name='issues-list'),
    url(r'^(?P<pk>[0-9]+)/$', IssueView.as_view(), name='issue'),
]
