from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, ListView, CreateView
from django.views import View
from django.views.generic.detail import SingleObjectMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
import datetime
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


class AddIssueView(LoginRequiredMixin, CreateView):
    model = Issue
    fields = ['title', 'content']
    template_name = 'add_issue.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(AddIssueView, self).form_valid(form)


class SetIssueStatusView(SingleObjectMixin, PermissionRequiredMixin, View):
    '''
    View that sets an Issue's 'approved' field to now.
    '''
    model = Issue
    permission_required = 'issues.can_update_status'
    raise_exception = True
    http_method_names = ['post']
    status_field = 'approved'

    def post(self, request, pk):
        issue = self.get_object()
        if getattr(issue, self.status_field) is None:
            setattr(issue, self.status_field, datetime.datetime.now())
            issue.save()
        return redirect(issue.get_absolute_url())
