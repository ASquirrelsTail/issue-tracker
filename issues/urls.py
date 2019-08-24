from django.conf.urls import url
from issues.views import IssuesListView, IssueView, AddIssueView

urlpatterns = [
    url(r'^$', IssuesListView.as_view(), name='issues-list'),
    url(r'^(?P<pk>[0-9]+)/$', IssueView.as_view(), name='issue'),
    url(r'^add/$', AddIssueView.as_view(), name='add-issue')
]
