from django.shortcuts import render
from django.views.generic import DetailView, ListView
from issues.models import Issue

# Create your views here.


class IssuesListView(ListView):
    model = Issue
    template_name = 'issue_list.html'


class IssueView(DetailView):
    queryset = Issue.objects.all()
    template_name = 'issue_detail.html'

    def get_object(self, queryset=None):
        issue = super(IssueView, self).get_object(queryset)
        issue.views += 1
        issue.save()
        return issue
