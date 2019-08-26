from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, ListView, CreateView, UpdateView
from django.views import View
from django.views.generic.detail import SingleObjectMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
import datetime
from issues.models import Issue, Comment, Vote
from issues.forms import CommentForm

# Create your views here.


class AuthorOrAdminMixin(PermissionRequiredMixin, SingleObjectMixin):
    '''
    Mixin for checking whether a user is the author of an object, or they have
    permission to access it. Otherwise returns 403 Forbidden.
    '''
    raise_exception = True

    def has_permission(self):
        return self.get_object().user == self.request.user or super(AuthorOrAdminMixin, self).has_permission()


class NotAuthorOrAdminMixin(AuthorOrAdminMixin):
    '''
    Mixin for checking a user ISN'T the author of the object or an admin.
    '''
    def has_permission(self):
        return not super(AuthorOrAdminMixin, self).has_permission()


class IssuesListView(ListView):
    '''
    List view for displaying issues.
    '''
    model = Issue
    template_name = 'issue_list.html'


class IssueView(DetailView):
    '''
    Detail view for displaying individual issues.
    Increases issue's view count and gets comments and votes on load.
    Inserts comment form and whether a user has voted already into 
    template context.
    '''
    queryset = Issue.objects.all()
    template_name = 'issue_detail.html'

    def get_object(self, queryset=None):
        issue = super(IssueView, self).get_object(queryset)
        issue.views += 1
        issue.save()
        issue.votes = issue.get_votes()
        issue.comments = issue.get_comments()
        return issue

    def get_context_data(self, **kwargs):
        context = super(IssueView, self).get_context_data(**kwargs)
        context['comment_form'] = CommentForm()
        context['has_voted'] = self.object.has_voted(self.request.user)
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


class EditIssueView(AuthorOrAdminMixin, UpdateView):
    '''
    View to edit a comment.
    Sets the edited date to now on save.
    '''
    permission_required = 'issues.can_edit_all_issues'
    model = Issue
    fields = ['title', 'content']
    template_name = 'edit_issue.html'

    def form_valid(self, form):
        form.instance.edited = datetime.datetime.now()
        return super(EditIssueView, self).form_valid(form)


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


class VoteForIssueView(SingleObjectMixin, LoginRequiredMixin, View):
    '''
    View to add a vote to an issue, if the user has not already voted for it.
    Redirects to issue page.
    '''
    model = Issue
    http_method_names = ['post']

    def post(self, request, pk):
        issue = self.get_object()
        if not issue.has_voted(request.user):
            vote = Vote(user=request.user, issue=issue)
            vote.save()
        return redirect(issue.get_absolute_url())


class AddCommentView(LoginRequiredMixin, CreateView):
    '''
    View to add a new comment to an issue.
    Sets the comment's user to the user making the request.
    Sets the comments issue to the referenced issue.
    Sets the comment's reply_to to the referenced comment.
    '''
    model = Comment
    form_class = CommentForm
    template_name = 'add_comment.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.issue = get_object_or_404(Issue, pk=int(self.kwargs['issue_pk']))
        if self.kwargs.get('comment_pk'):
            form.instance.reply_to = get_object_or_404(Comment, pk=int(self.kwargs['comment_pk']))
        return super(AddCommentView, self).form_valid(form)


class EditCommentView(AuthorOrAdminMixin, UpdateView):
    '''
    View to edit a comment.
    Sets the edited date to now on save.
    '''
    permission_required = 'issues.can_edit_all_comments'
    model = Comment
    form_class = CommentForm
    template_name = 'edit_comment.html'

    def form_valid(self, form):
        form.instance.edited = datetime.datetime.now()
        return super(EditCommentView, self).form_valid(form)
