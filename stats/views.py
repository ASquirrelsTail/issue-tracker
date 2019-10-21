from django.views.generic.base import TemplateView, ContextMixin
from django.views.generic import DetailView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Avg, Sum, Count, TextField, DateField, DurationField, F
from django.db.models.functions import Cast, TruncDay
from django.utils import timezone
from datetime import timedelta
import json
from collections import OrderedDict
from tickets.models import Ticket, Pageview, Vote, Comment
from tickets.views import AuthorOrAdminMixin
from credits.models import Credit, Debit
from stats.forms import DateRangeForm


def filter_date_range(queryset, status, start=None, end=None):
    '''
    Filters a queryset for a given status between a date range
    '''
    query = {}
    if start:
        query[status + '__date__gte'] = start
    if end:
        query[status + '__date__lte'] = end
    if query != {}:
        return queryset.filter(**query)
    else:
        return queryset


def last_x_days(queryset, status, days):
    '''
    Function for filtering a queryset for a given status being set in the last X days.
    '''
    start_date = timezone.now().date() - timedelta(days=days)
    return filter_date_range(queryset, status, start=start_date)


def annotate_date(queryset, status, field_name='date'):
    '''
    Annotates queryset with a 'date' field, created from the chosen status.
    '''
    annotation = {field_name: Cast(TruncDay(status, DateField()), TextField())}
    return queryset.annotate(**annotation)


def avg_time_taken(queryset, start_status, end_status):
    '''
    Returns a timedelta of the avg time taken between two statuses in a given queryset.
    '''
    return queryset.exclude(**{end_status: None}).annotate(time_taken=F(end_status) - F(start_status)).aggregate(Avg('time_taken'))['time_taken__avg']


def interval_string(interval):
    '''
    Converts a timedelta interval to a string of years, months, weeks, days, hours, minutes.
    '''
    intervals = (
        ('year', timedelta(days=365).total_seconds()),
        ('month', timedelta(days=30).total_seconds()),
        ('week', timedelta(days=7).total_seconds()),
        ('day', timedelta(days=1).total_seconds()),
        ('hour', timedelta(hours=1).total_seconds()),
        ('minute', timedelta(minutes=1).total_seconds()),
    )

    seconds = interval.total_seconds()
    result = ''

    for interval_name, interval_seconds in intervals:
        if seconds >= interval_seconds:
            count = seconds // interval_seconds
            seconds %= interval_seconds
            result += '{:.0f} {}{} '.format(count, interval_name, 's' if count > 1 else '')

    return result


class IndexView(TemplateView, ContextMixin):
    '''
    View for index page.
    '''
    template_name = 'index.html'

    def get_context_data(self):
        context = super(IndexView, self).get_context_data()
        context['bugs_this_week'] = last_x_days(Ticket.objects.filter(ticket_type='Bug'), 'done', 7).count()
        context['features_coming_soon'] = Ticket.objects.exclude(doing=None).filter(ticket_type='Feature', done=None).count()
        avg_time_to_bugfix = avg_time_taken(Ticket.objects.filter(ticket_type='Bug'), 'created', 'done')
        context['avg_time_to_bugfix'] = interval_string(avg_time_to_bugfix)
        try:
            context['most_requested_feature_url'] = Ticket.objects.exclude(approved=None, done=None).annotate(votes=Sum('vote__count')).order_by('votes')[0].get_absolute_url()
        except (IndexError, Ticket.DoesNotExist):
            context['most_requested_feature_url'] = None
        return context


class DateRangeView(ContextMixin):
    '''
    Abstract view for including date range queries for stats.
    '''
    date_to_use = 'created'

    def get_form_kwargs(self):
        self.form = DateRangeForm(self.request.GET)
        self.form.is_valid()

    def get_date_range_and_annotate(self, queryset, total=Count('date')):
        '''
        Filters the queryset by the date range, annotates the queryset with a date field base don the date_to_use (default 'created'),
        groups the queryset by date, and annotates it with a total, based on the total annotation provided (default count).
        '''
        queryset = filter_date_range(queryset, self.date_to_use, self.form.cleaned_data.get('start_date'), self.form.cleaned_data.get('end_date'))
        queryset = annotate_date(queryset, self.date_to_use)
        queryset = queryset.values('date').annotate(total=total)
        return queryset

    def get_context_data(self, **kwargs):
        self.get_form_kwargs()
        context = super(DateRangeView, self).get_context_data(**kwargs)
        context['date_range_form'] = self.form

        return context


class TicketStatsView(AuthorOrAdminMixin, DateRangeView, DetailView):
    '''
    View for ticket stats, only accessible by a tickets author, or admin with the required permission.
    '''
    queryset = Ticket.objects.all()
    permission_required = 'tickets.can_view_all_stats'
    raise_exception = True
    template_name = 'ticket_stats_detail.html'

    def get_context_data(self, **kwargs):
        context = super(TicketStatsView, self).get_context_data(**kwargs)

        # Add stats to page context
        chart_data = {}
        chart_data['comments'] = list(self.get_date_range_and_annotate(self.object.comment_set))
        chart_data['views'] = list(self.get_date_range_and_annotate(self.object.pageview_set))
        chart_data['votes'] = list(self.get_date_range_and_annotate(self.object.vote_set, total=Sum('count')))

        context['chart_data'] = json.dumps(chart_data)

        return context


class AllTicketStatsView(PermissionRequiredMixin, TemplateView, DateRangeView):
    '''
    View for displaying stats across all tickets. Only accessible to admin users.
    '''
    permission_required = 'tickets.can_view_all_stats'
    raise_exception = True
    template_name = 'ticket_stats_all.html'

    def get_context_data(self, **kwargs):
        context = super(AllTicketStatsView, self).get_context_data(**kwargs)

        context['awaiting_approval'] = Ticket.objects.filter(approved=None).count()
        context['top_5_features'] = Ticket.objects.exclude(approved=None).filter(ticket_type='Feature', done=None).annotate(votes=Sum('vote__count')).order_by('-votes')[:5]
        context['top_5_bugs'] = Ticket.objects.exclude(approved=None).filter(ticket_type='Bug', done=None).annotate(votes=Sum('vote__count')).order_by('-votes')[:5]

        chart_data = {}
        chart_data['bugs'] = list(self.get_date_range_and_annotate(Ticket.objects.filter(ticket_type='Bug')))
        chart_data['features'] = list(self.get_date_range_and_annotate(Ticket.objects.filter(ticket_type='Feature')))
        chart_data['comments'] = list(self.get_date_range_and_annotate(Comment.objects.all()))
        chart_data['views'] = list(self.get_date_range_and_annotate(Pageview.objects.all()))
        chart_data['votes'] = list(self.get_date_range_and_annotate(Vote.objects.all(), total=Sum('count')))

        context['chart_data'] = json.dumps(chart_data)

        return context


class TransactionsStatsView(PermissionRequiredMixin, TemplateView, DateRangeView):
    '''
    View for displaying stats across all transactions. Only accessible to admin users.
    '''
    permission_required = 'credits.can_view_transactions_stats'
    raise_exception = True
    template_name = 'transaction_stats.html'

    def get_context_data(self, **kwargs):
        context = super(TransactionsStatsView, self).get_context_data(**kwargs)

        chart_data = {}
        chart_data['credit'] = list(self.get_date_range_and_annotate(Credit.objects.filter(real_value__gte=1), total=Sum('real_value')))
        chart_data['debit'] = list(self.get_date_range_and_annotate(Debit.objects.filter(real_value__gte=1), total=Sum('real_value')))

        context['chart_data'] = json.dumps(chart_data)

        return context


class RoadmapView(TemplateView, ContextMixin):
    '''
    View for displaying roadmap with features and bugs with statuses of done and doing.
    '''
    template_name = 'roadmap.html'

    def get_context_data(self, **kwargs):
        context = super(RoadmapView, self).get_context_data(**kwargs)

        context['bugs'] = Ticket.objects.filter(ticket_type='Bug').exclude(doing=None).extra(select={'is_doing': 'done IS NULL'}).extra(order_by=['-is_doing', '-done'])
        context['features'] = Ticket.objects.filter(ticket_type='Feature').exclude(doing=None).extra(select={'is_doing': 'done IS NULL'}).extra(order_by=['-is_doing', '-done'])

        return context
