from django.conf.urls import url, include
from issues.views import IssueView

urlpatterns = [
    url(r'^(?P<pk>[0-9]+)/$', IssueView.as_view(), name='issues'),
]
