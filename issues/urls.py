from django.conf.urls import url
from issues.views import IssuesListView, IssueView, AddIssueView, SetIssueStatusView, AddCommentView, EditCommentView, EditIssueView

urlpatterns = [
    url(r'^$', IssuesListView.as_view(), name='issues-list'),
    url(r'^(?P<pk>[0-9]+)/$', IssueView.as_view(), name='issue'),
    url(r'^(?P<pk>[0-9]+)/approved/$', SetIssueStatusView.as_view(status_field='approved'), name='approve-issue'),
    url(r'^(?P<pk>[0-9]+)/doing/$', SetIssueStatusView.as_view(status_field='doing'), name='doing-issue'),
    url(r'^(?P<pk>[0-9]+)/done/$', SetIssueStatusView.as_view(status_field='done'), name='done-issue'),
    url(r'^add/$', AddIssueView.as_view(), name='add-issue'),
    url(r'^(?P<pk>[0-9]+)/edit/$', EditIssueView.as_view(), name='edit-issue'),
    url(r'^(?P<issue_pk>[0-9]+)/comments/add/$', AddCommentView.as_view(), name='add-comment'),
    url(r'^(?P<issue_pk>[0-9]+)/comments/(?P<comment_pk>[0-9]+)/reply/$', AddCommentView.as_view(), name='add-reply'),
    url(r'^(?P<issue_pk>[0-9]+)/comments/(?P<pk>[0-9]+)/edit/$', EditCommentView.as_view(), name='edit-comment'),
]
