from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, ListView, CreateView
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
