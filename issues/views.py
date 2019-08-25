from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, ListView, CreateView
from django.views import View
from django.views.generic.detail import SingleObjectMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
import datetime
from issues.models import Issue, Comment
from issues.forms import CommentForm

# Create your views here.


class IssuesListView(ListView):
    '''
    List view for displaying issues.
    '''
    model = Issue
    template_name = 'issue_list.html'


class IssueView(DetailView):
    '''
    Detail view for displaying individual issues.
    Increases issue's view count on load.
    '''
    queryset = Issue.objects.all()
    template_name = 'issue_detail.html'

    def get_object(self, queryset=None):
        issue = super(IssueView, self).get_object(queryset)
        issue.views += 1
        issue.save()
        issue.comments = issue.comment_set.all()
        return issue

    def get_context_data(self, **kwargs):
        context = super(IssueView, self).get_context_data(**kwargs)
        context['comment_form'] = CommentForm()
        return context


class AddIssueView(LoginRequiredMixin, CreateView):
    '''
    View to add a new issue with title and content.
    Sets the issue's user to the user making the request.
    '''
    model = Issue
    fields = ['title', 'content']
    template_name = 'add_issue.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(AddIssueView, self).form_valid(form)


class SetIssueStatusView(SingleObjectMixin, PermissionRequiredMixin, View):
    '''
    View that sets an Issue's status field to now.
    Can only be accessed by users with the can_update_status permission.
    '''
    model = Issue
    permission_required = 'issues.can_update_status'
    raise_exception = True
    http_method_names = ['post']
    status_field = 'approved'

    def post(self, request, pk):
        '''
        On Post sets the given status field of an issue to the current time, if it is not already set.
        Redirects to the issue's page.
        '''
        issue = self.get_object()
        if getattr(issue, self.status_field) is None:
            setattr(issue, self.status_field, datetime.datetime.now())
            issue.save()
        return redirect(issue.get_absolute_url())


class AddCommentView(LoginRequiredMixin, CreateView):
    '''
    View to add a new comment to an issue.
    Sets the comment's user to the user making the request.
    Sets the comments issue to the referenced issue.
    Sets the comment's reply_to to the referenced comment.
    '''
    model = Comment
    fields = ['content']
    template_name = 'add_comment.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.issue = get_object_or_404(Issue, pk=int(self.kwargs['issue_pk']))
        if self.kwargs.get('comment_pk'):
            form.instance.reply_to = get_object_or_404(Comment, pk=int(self.kwargs['comment_pk']))
        return super(AddCommentView, self).form_valid(form)
