from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import DetailView, ListView, CreateView, UpdateView, DeleteView
from django.views import View
from django.views.generic.detail import SingleObjectMixin
from django.utils import timezone
from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.urls import reverse_lazy
from tickets.models import Ticket, Comment, Vote, Pageview
from tickets.forms import CommentForm, TicketForm


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
    queryset = Ticket.objects.all().order_by('-created')
    template_name = 'ticket_list.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super(TicketsListView, self).get_context_data(**kwargs)
        context['page_range'] = range(max(min(context['page_obj'].number - 2, context['paginator'].num_pages - 4), 1),
                                      min(max(context['page_obj'].number + 2, 5), context['paginator'].num_pages) + 1)
        return context


class TicketView(DetailView):
    '''
    Detail view for displaying individual tickets.
    Increases ticket's view count and gets comments and votes on load.
    Inserts comment form and whether a user has voted already into
    template context.
    '''
    queryset = Ticket.objects.all()
    template_name = 'ticket_detail.html'

    def get_object(self, queryset=None):
        ticket = super(TicketView, self).get_object(queryset)
        # If ticket hasn't already been viewed this session, create a new pageview for it.
        if not self.request.session.get('ticket-{}-viewed'.format(ticket.id), False):
            view = Pageview(ticket=ticket)
            view.save()
            self.request.session['i{}'.format(ticket.id)] = True
        return ticket

    def get_context_data(self, **kwargs):
        context = super(TicketView, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['comment_form'] = CommentForm()
            context['has_voted'] = self.object.has_voted(self.request.user)
        return context


class AddTicketView(LoginRequiredMixin, CreateView):
    '''
    View to add a new ticket with title and content.
    Sets the ticket's user to the user making the request.
    '''
    model = Ticket
    form_class = TicketForm
    template_name = 'add_ticket.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(AddTicketView, self).form_valid(form)


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
        return super(EditTicketView, self).form_valid(form)


class DeleteTicketView(AuthorOrAdminMixin, DeleteView):
    permission_required = 'tickets.can_edit_all_tickets'
    model = Ticket
    success_url = reverse_lazy('tickets-list')
    template_name = 'delete_ticket.html'


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
        ticket.set_status(self.status_field)
        return redirect(ticket.get_absolute_url())


class VoteForTicketView(SingleObjectMixin, LoginRequiredMixin, View):
    '''
    View to add a vote to an ticket, if the user has not already voted for it.
    Redirects to ticket page.
    '''
    model = Ticket
    http_method_names = ['post']
    raise_exception = True

    def post(self, request, pk):
        ticket = self.get_object()
        if ticket.vote(request.user):
            return redirect(ticket.get_absolute_url())
        else:
            raise PermissionDenied


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
