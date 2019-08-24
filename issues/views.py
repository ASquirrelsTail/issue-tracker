from django.shortcuts import render
from django.views.generic import DetailView
from issues.models import Issue

# Create your views here.


class IssueView(DetailView):
    queryset = Issue.objects.all()
    template_name = 'issue_detail.html'
