from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import DetailView, ListView, CreateView, UpdateView, DeleteView
from django.views import View
from django.views.generic.detail import SingleObjectMixin
from django.utils import timezone
from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.urls import reverse_lazy
from issues.models import Issue, Comment, Vote, Pageview
from issues.forms import CommentForm, IssueForm


# MIXINS #

class AuthorOrAdminMixin(PermissionRequiredMixin, SingleObjectMixin):
    '''
    Mixin for checking whether a user is the author of an object, or they have
    permission to access it. Otherwise returns 403 Forbidden.
    '''
    raise_exception = True

    def has_permission(self):
        return self.get_object().user == self.request.user or super(AuthorOrAdminMixin, self).has_permission()


# ISSUE VIEWS #

class IssuesListView(ListView):
    '''
    List view for displaying issues.
    '''
    queryset = Issue.objects.all().order_by('-created')
    template_name = 'issue_list.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super(IssuesListView, self).get_context_data(**kwargs)
        context['page_range'] = range(max(min(context['page_obj'].number - 2, context['paginator'].num_pages - 4), 1),
                                      min(max(context['page_obj'].number + 2, 5), context['paginator'].num_pages) + 1)
        return context


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
        # If issue hasn't already been viewed this session, create a new pageview for it.
        if not self.request.session.get('issue-{}-viewed'.format(issue.id), False):
            view = Pageview(issue=issue)
            view.save()
            self.request.session['i{}'.format(issue.id)] = True
        return issue

    def get_context_data(self, **kwargs):
        context = super(IssueView, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['comment_form'] = CommentForm()
            context['has_voted'] = self.object.has_voted(self.request.user)
        return context


class AddIssueView(LoginRequiredMixin, CreateView):
    '''
    View to add a new issue with title and content.
    Sets the issue's user to the user making the request.
    '''
    model = Issue
    form_class = IssueForm
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
    form_class = IssueForm
    template_name = 'edit_issue.html'

    def form_valid(self, form):
        form.instance.edited = timezone.now()
        return super(EditIssueView, self).form_valid(form)


class DeleteIssueView(AuthorOrAdminMixin, DeleteView):
    permission_required = 'issues.can_edit_all_issues'
    model = Issue
    success_url = reverse_lazy('issues-list')
    template_name = 'delete_issue.html'


class SetIssueStatusView(SingleObjectMixin, PermissionRequiredMixin, View):
    '''
    View that sets an Issue's status to the given status_field.
    Can only be accessed by users with the can_update_status permission.
    '''
    model = Issue
    permission_required = 'issues.can_update_status'
    raise_exception = True
    http_method_names = ['post']
    status_field = None

    def post(self, request, pk):
        issue = self.get_object()
        issue.set_status(self.status_field)
        return redirect(issue.get_absolute_url())


class VoteForIssueView(SingleObjectMixin, LoginRequiredMixin, View):
    '''
    View to add a vote to an issue, if the user has not already voted for it.
    Redirects to issue page.
    '''
    model = Issue
    http_method_names = ['post']
    raise_exception = True

    def post(self, request, pk):
        issue = self.get_object()
        if not issue.has_voted(request.user):
            vote = Vote(user=request.user, issue=issue)
            vote.save()
            return redirect(issue.get_absolute_url())
        else:
            raise PermissionDenied


# COMMENT VIEWS #

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
    raise_exception = True

    def get_context_data(self, **kwargs):
        context = super(AddCommentView, self).get_context_data(**kwargs)
        context['issue'] = get_object_or_404(Issue, pk=int(self.kwargs['issue_pk']))
        if self.kwargs.get('comment_pk'):
            context['reply_to'] = get_object_or_404(Comment, pk=int(self.kwargs['comment_pk']))
            if context['reply_to'].issue.id != context['issue'].id or context['reply_to'].reply_to is not None:
                raise SuspiciousOperation
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.issue = get_object_or_404(Issue, pk=int(self.kwargs['issue_pk']))
        if self.kwargs.get('comment_pk'):
            form.instance.reply_to = get_object_or_404(Comment, pk=int(self.kwargs['comment_pk']))
            if form.instance.reply_to.issue.id != form.instance.issue.id or form.instance.reply_to.reply_to is not None:
                raise SuspiciousOperation
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
    raise_exception = True

    def get_context_data(self, **kwargs):
        context = super(EditCommentView, self).get_context_data(**kwargs)
        context['issue'] = get_object_or_404(Issue, pk=int(self.kwargs['issue_pk']))
        return context

    def form_valid(self, form):
        form.instance.edited = timezone.now()
        return super(EditCommentView, self).form_valid(form)
