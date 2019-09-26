from django.views.generic.base import TemplateView, ContextMixin
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Avg, Sum, TextField, DateField
from django.db.models.functions import Cast, TruncDay
from django.utils import timezone
from datetime import timedelta
from tickets.models import Ticket, Pageview, Vote, Comment
from tickets.views import AuthorOrAdminMixin
from stats.forms import DateRangeForm


def last_x_days(queryset, status, days):
    '''
    Function for filtering a queryset for a given status being set in the last X days.
    '''
    x_days = timedelta(days=days)
    query = {status + '__gte': timezone.now() - x_days}
    queryset = queryset.filter(**query)
    return queryset


class IndexView(TemplateView, ContextMixin):
    '''
    View for index page.
    '''
    template_name = 'index.html'

    def get_context_data(self):
        context = super(IndexView, self).get_context_data()
        context['bugs_this_week'] = last_x_days(Ticket.objects.filter(ticket_type='Bug'), 'done', 7).count()
        context['features_coming_soon'] = Ticket.objects.exclude(doing=None).filter(ticket_type='Feature', done=None).count()
        # avg_bug_creation = Ticket.objects.exclude(done=None).aggregate(Avg('created'))['created_avg']
        # avg_bug_completion = Ticket.objects.exclude(done=None).aggregate(Avg('done'))['done_avg']
        # avg_bug_time_taken = avg_bug_completion - avg_bug_creation
        # context['avg_time_to_bugfix'] = str(avg_bug_time_taken)
        try:
            context['most_requested_feature_url'] = Ticket.objects.exclude(approved=None, done=None).annotate(votes=Sum('vote__count')).order_by('votes')[0].get_absolute_url()
        except Ticket.DoesNotExist:
            context['most_requested_feature_url'] = None
        return context


class TicketStatsView(AuthorOrAdminMixin, DetailView):
    '''
    View for ticket stats, only accessible by a tickets author, or admin with the required permission.
    '''
    queryset = Ticket.objects.all()
    template_name = 'ticket_stats_detail.html'
    permission_required = 'tickets.can_view_all_stats'

    def get_form_kwargs(self):
        self.form = DateRangeForm(self.request.GET)
        self.form.is_valid()

    def get_date_range(self, queryset):
        if self.form.cleaned_data['start_date']:
            queryset = queryset.filter(created__date__gte=self.form.cleaned_data['start_date'])
        if self.form.cleaned_data['end_date']:
            queryset = queryset.filter(created__date__lte=self.form.cleaned_data['end_date'])
        return queryset

    def get_context_data(self, **kwargs):
        context = super(TicketStatsView, self).get_context_data(**kwargs)

        # Add stats to page context
        context['comments'] = self.get_date_range(self.object.comment_set).annotate(date=Cast(TruncDay('created', DateField()), TextField())).values('date')
        context['views'] = self.get_date_range(self.object.pageview_set).annotate(date=Cast(TruncDay('created', DateField()), TextField())).values('date')
        context['votes'] = self.get_date_range(self.object.vote_set).annotate(date=Cast(TruncDay('created', DateField()), TextField())).values('date', 'count')

        context['date_range_form'] = self.form
        context['ticket_url'] = self.object.get_absolute_url()

        return context

    def get(self, request, pk):
        self.get_form_kwargs()
        return super(TicketStatsView, self).get(request, pk)
