from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import DetailView, ListView, CreateView, UpdateView, DeleteView
from django.views import View
from django.views.generic.detail import SingleObjectMixin
from django.utils import timezone
from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q, Count, Sum
from django.http import HttpResponseBadRequest
from tickets.models import Ticket, Comment, Pageview
from tickets.forms import CommentForm, TicketForm, FeatureForm, BugForm, VoteForm, FilterForm


# MIXINS #

class AuthorOrAdminMixin(PermissionRequiredMixin, SingleObjectMixin):
    '''
    Mixin for checking whether a user is the author of an object, or they have
    permission to access it. Otherwise returns 403 Forbidden.
    '''
    raise_exception = True

    def has_permission(self):
        return self.get_object().user == self.request.user or super(AuthorOrAdminMixin, self).has_permission()


# TICKET VIEWS #

class TicketsListView(ListView):
    '''
    List view for displaying tickets.
    '''
    queryset = Ticket.objects.all()
    template_name = 'ticket_list.html'
    paginate_by = 10

    def get_form_kwargs(self):
        self.form = FilterForm(self.request.GET)

    def get_queryset(self):
        queryset = super(TicketsListView, self).get_queryset()

        if not self.request.user.is_authenticated:  # If user is not authenticated exclude tickets awaiting approval.
            queryset = queryset.exclude(approved=None)
        else:
            # If user is not admin exclude tickets awaiting approval thet they are not the author of.
            if not self.request.user.has_perm('tickets.can_update_status'):
                queryset = queryset.exclude(Q(approved=None) & ~Q(user=self.request.user))

        if self.form.is_valid():
            filters = self.form.cleaned_data
            if filters['ticket_type'] != '':
                queryset = queryset.filter(ticket_type=filters['ticket_type'])
            # If ticket status specified, filter for that status by filtering for the following status being unset
            # and excluding the current status being none.
            if filters['status'] != '':
                if filters['status'] == 'awaiting':
                    queryset = queryset.filter(approved=None)
                elif filters['status'] == 'approved':
                    queryset = queryset.filter(doing=None).exclude(approved=None)
                elif filters['status'] == 'doing':
                    queryset = queryset.filter(done=None).exclude(doing=None)
                elif filters['status'] == 'done':
                    queryset = queryset.exclude(done=None)

            if filters['order_by']:
                if filters['order_by'] != 'created':
                    queryset = queryset.annotate(views=Count('pageview'), votes=Sum('vote__count'), comment_count=Count('comment'))
                queryset = queryset.order_by(filters['order_by'])

        return queryset

    def get_context_data(self, **kwargs):
        context = super(TicketsListView, self).get_context_data(**kwargs)

        # Build query string for pagination
        queries = []
        for key, value in self.form.cleaned_data.items():
            if value != '':
                queries.append(key + '=' + value)
        queries.append('page=')
        context['query_string'] = '?' + '&'.join(queries)

        # Work out range of pages to show in pagination. Max of 5, +- 2 pages in each direction if possible, otherwise up to +- 4 at ends of range.
        context['page_range'] = range(max(min(context['page_obj'].number - 2, context['paginator'].num_pages - 4), 1),
                                      min(max(context['page_obj'].number + 2, 5), context['paginator'].num_pages) + 1)

        context['no_tickets'] = self.get_queryset().count()

        context['filter_form'] = self.form

        return context

    def get(self, request):
        self.get_form_kwargs()
        return super(TicketsListView, self).get(request)


class TicketView(AuthorOrAdminMixin, DetailView):
    '''
    Detail view for displaying individual tickets.
    Increases ticket's view count and gets comments and votes on load.
    Inserts comment form and whether a user has voted already into
    template context.
    '''
    queryset = Ticket.objects.all()
    template_name = 'ticket_detail.html'
    permission_required = 'tickets.can_update_status'

    def get_object(self, queryset=None):
        ticket = super(TicketView, self).get_object(queryset)
        # If ticket hasn't already been viewed this session, create a new pageview for it.
        if not self.request.session.get('ticket-{}-viewed'.format(ticket.id), False):
            view = Pageview(ticket=ticket)
            view.save()
            self.request.session['ticket-{}-viewed'.format(ticket.id)] = True
        return ticket

    def has_permission(self):
        '''
        If a ticket is awaiting approval, it can only be viewed by the user that created it,
        and admins with permission to update a ticket's status.
        '''
        if self.get_object().approved is None:
            return super(TicketView, self).has_permission()
        else:
            return True

    def get_context_data(self, **kwargs):
        '''
        Add comment form and vote form where necessary.
        '''
        context = super(TicketView, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated and self.object.approved:
            context['comment_form'] = CommentForm()
            context['has_voted'] = self.object.has_voted(self.request.user)
            if self.object.ticket_type == 'Feature':
                context['vote_form'] = VoteForm()
        return context


class AddTicketView(LoginRequiredMixin, CreateView):
    '''
    View to add a new ticket with title and content.
    Sets the ticket's user to the user making the request, and notifies success if valid.
    '''
    model = Ticket
    success_message = 'Successfully created ticket.'
    form_class = TicketForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, self.success_message)
        return super(AddTicketView, self).form_valid(form)


class AddBugView(AddTicketView):
    '''
    View to submit a bug report.
    '''
    success_message = 'Successfully submitted bug report.'
    form_class = BugForm
    template_name = 'add_bug.html'


class AddFeatureView(AddTicketView):
    '''
    View to submit a feature request.
    '''
    success_message = 'Successfully submitted feature request.'
    form_class = FeatureForm
    template_name = 'add_feature.html'


class EditTicketView(AuthorOrAdminMixin, UpdateView):
    '''
    View to edit a comment.
    Sets the edited date to now on save.
    '''
    permission_required = 'tickets.can_edit_all_tickets'
    model = Ticket
    form_class = TicketForm
    template_name = 'edit_ticket.html'

    def form_valid(self, form):
        form.instance.edited = timezone.now()
        messages.success(self.request, 'Successfully edited ticket.')
        return super(EditTicketView, self).form_valid(form)


class DeleteTicketView(AuthorOrAdminMixin, DeleteView):
    '''
    View to delete a ticket.
    '''
    permission_required = 'tickets.can_edit_all_tickets'
    model = Ticket
    success_url = reverse_lazy('tickets-list')
    template_name = 'delete_ticket.html'

    def get_success_url(self):
        messages.success(self.request, 'Successfully deleted ticket.')
        return super(DeleteTicketView, self).get_success_url()


class SetTicketStatusView(SingleObjectMixin, PermissionRequiredMixin, View):
    '''
    View that sets an Ticket's status to the given status_field.
    Can only be accessed by users with the can_update_status permission.
    '''
    model = Ticket
    permission_required = 'tickets.can_update_status'
    raise_exception = True
    http_method_names = ['post']
    status_field = None

    def post(self, request, pk):
        ticket = self.get_object()
        result = ticket.set_status(self.status_field)
        if result:
            messages.success(self.request, 'Ticket status set to {}.'.format(result))
        else:
            messages.error(self.request, 'Failed to update ticket status.')
        return redirect(ticket.get_absolute_url())


class VoteForTicketView(SingleObjectMixin, LoginRequiredMixin, View):
    '''
    View to add a vote to a ticket, gets credits to spend on vote from submitted form
    if type is feature. Posts success message and redirects to ticket page.
    '''
    model = Ticket
    http_method_names = ['post']
    raise_exception = True

    def post(self, request, pk):
        credits = 1
        ticket = self.get_object()
        if ticket.ticket_type == 'Feature':
            # If ticket is feature request, validate the vote form and get the credits to spend on vote.
            vote_form = VoteForm(request.POST)
            if vote_form.is_valid():
                credits = vote_form.cleaned_data['credits']
            else:
                return HttpResponseBadRequest()
        vote = ticket.vote(request.user, credits)
        if vote['success']:
            messages.success(self.request, vote['message'])
        else:
            messages.error(self.request, vote['message'])
        return redirect(ticket.get_absolute_url())


# COMMENT VIEWS #

class AddCommentView(LoginRequiredMixin, CreateView):
    '''
    View to add a new comment to an ticket.
    Sets the comment's user to the user making the request.
    Sets the comments ticket to the referenced ticket.
    Sets the comment's reply_to to the referenced comment.
    '''
    model = Comment
    form_class = CommentForm
    template_name = 'add_comment.html'
    raise_exception = True

    def get_context_data(self, **kwargs):
        context = super(AddCommentView, self).get_context_data(**kwargs)
        context['ticket'] = get_object_or_404(Ticket, pk=int(self.kwargs['ticket_pk']))
        if self.kwargs.get('comment_pk'):
            context['reply_to'] = get_object_or_404(Comment, pk=int(self.kwargs['comment_pk']))
            if context['reply_to'].ticket.id != context['ticket'].id or context['reply_to'].reply_to is not None:
                raise SuspiciousOperation
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.ticket = get_object_or_404(Ticket, pk=int(self.kwargs['ticket_pk']))
        if self.kwargs.get('comment_pk'):
            form.instance.reply_to = get_object_or_404(Comment, pk=int(self.kwargs['comment_pk']))
            if form.instance.reply_to.ticket.id != form.instance.ticket.id or form.instance.reply_to.reply_to is not None:
                raise SuspiciousOperation
        return super(AddCommentView, self).form_valid(form)


class EditCommentView(AuthorOrAdminMixin, UpdateView):
    '''
    View to edit a comment.
    Sets the edited date to now on save.
    '''
    permission_required = 'tickets.can_edit_all_comments'
    model = Comment
    form_class = CommentForm
    template_name = 'edit_comment.html'
    raise_exception = True

    def get_context_data(self, **kwargs):
        context = super(EditCommentView, self).get_context_data(**kwargs)
        context['ticket'] = get_object_or_404(Ticket, pk=int(self.kwargs['ticket_pk']))
        return context

    def form_valid(self, form):
        form.instance.edited = timezone.now()
        return super(EditCommentView, self).form_valid(form)
