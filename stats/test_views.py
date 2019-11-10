from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User, Permission
from django.utils import timezone
from django.db.models import Sum, Max
from datetime import timedelta, datetime, date
from tickets.models import Ticket, Comment, Vote, Pageview
from credits.models import Credit, Debit
from stats.views import interval_string, filter_date_range, annotate_date, RoadmapView, DateRangeMixin
from stats.forms import DateRangeForm
import json


class FilterDateRangeTestCase(TestCase):
    '''
    Tests for filter_date_range.
    '''
    @classmethod
    def setUpTestData(cls):
        test_user = User.objects.create_user(username='TestUser', email='test@test.com',
                                             password='tH1$isA7357')
        test_user.save()

        for day in range(45):
            daily_ticket = Ticket.objects.create(user=test_user, title='Day {}'.format(day), content='Test ticket')
            daily_ticket.created = timezone.now() - timedelta(days=60 - day)
            daily_ticket.approved = timezone.now() - timedelta(days=45 - day)
            daily_ticket.save()

    def test_returns_objects_after_start_date(self):
        '''
        The function should return a queryset comprising of only objects for which the selected status is on or after the start date.
        '''
        self.assertQuerysetEqual(filter_date_range(Ticket.objects.all(), 'created', start=timezone.now() - timedelta(days=20)),
                                 Ticket.objects.filter(created__date__gte=timezone.now() - timedelta(days=20)),
                                 transform=lambda x: x)

    def test_returns_objects_before_end_date(self):
        '''
        The function should return a queryset comprising of only objects for which the selected status is on or before the end date.
        '''
        self.assertQuerysetEqual(filter_date_range(Ticket.objects.all(), 'created', end=timezone.now() - timedelta(days=20)),
                                 Ticket.objects.filter(created__date__lte=timezone.now() - timedelta(days=20)),
                                 transform=lambda x: x)

    def test_returns_objects_between_start_and_end_date(self):
        '''
        The function should return objects between the start and end date.
        '''
        self.assertQuerysetEqual(filter_date_range(Ticket.objects.all(), 'created', start=timezone.now() - timedelta(days=30),
                                                   end=timezone.now() - timedelta(days=20)),
                                 Ticket.objects.filter(created__date__gte=timezone.now() - timedelta(days=30),
                                                       created__date__lte=timezone.now() - timedelta(days=20)),
                                 transform=lambda x: x)

    def test_no_start_or_end(self):
        '''
        If no start or end date is set the function should return the same queryset.
        '''
        self.assertQuerysetEqual(filter_date_range(Ticket.objects.all(), 'created'),
                                 Ticket.objects.all(),
                                 transform=lambda x: x)

    def test_filters_using_named_field(self):
        '''
        The function filters using the named status field.
        '''
        self.assertQuerysetEqual(filter_date_range(Ticket.objects.all(), 'approved', start=timezone.now() - timedelta(days=20)),
                                 Ticket.objects.filter(approved__date__gte=timezone.now() - timedelta(days=20)),
                                 transform=lambda x: x)


class AnnotateDateTestCase(TestCase):
    '''
    Adds rounded date annotation based off specified date field.
    '''

    @classmethod
    def setUpTestData(cls):
        test_user = User.objects.create_user(username='TestUser', email='test@test.com',
                                             password='tH1$isA7357')
        test_user.save()

        for hour in range(12):
            hourly_ticket = Ticket.objects.create(user=test_user, title='Test ticket', content='Test ticket')
            hourly_ticket.created = hourly_ticket.created.replace(hour=hour)
            hourly_ticket.save()

    def test_adds_date_annotation(self):
        '''
        Function should add rounded date annotation based off specified date field.
        '''
        self.assertRegex(annotate_date(Ticket.objects.all(), 'created')[0].date, '^[0-9]{4}-[0-9]{2}-[0-9]{2}$')

    def test_dates_same_day(self):
        '''
        Function should create date values for objects on the same day that are identical. This test is because PostgreSQL
        returns full datetimes, as opposed to just the dates returned by SQLite.
        '''
        self.assertEqual(annotate_date(Ticket.objects.all(), 'created')[0].date, annotate_date(Ticket.objects.all(), 'created')[11].date)


class IntervalStringTestCase(TestCase):
    '''
    Tests for interval string function, which composes a string.
    '''
    def test_returns_string_of_two_largest_values(self):
        '''
        Interval string should convert a timedelta to its two largest components in years, months, days, hours and minutes
        and return a string.
        '''
        self.assertEqual('2 years 3 months', interval_string(timedelta(days=833, hours=12, minutes=3)))
        self.assertEqual('3 months 13 days', interval_string(timedelta(days=103, hours=12, minutes=3)))
        self.assertEqual('12 hours 3 minutes', interval_string(timedelta(hours=12, minutes=3, seconds=30)))

    def test_returns_single_value(self):
        '''
        Should contain only one value if that's all there is.
        '''
        self.assertEqual('2 months', interval_string(timedelta(days=60)))
        self.assertEqual('3 days', interval_string(timedelta(days=3)))

    def test_returns_plurals(self):
        '''
        Strings should have plural values only when needed.
        '''
        self.assertEqual('3 days', interval_string(timedelta(days=3)))
        self.assertEqual('1 day', interval_string(timedelta(days=1)))
        self.assertEqual('3 minutes', interval_string(timedelta(minutes=3)))
        self.assertEqual('1 minute', interval_string(timedelta(minutes=1)))


class TestIndexTestCase(TestCase):
    '''
    Class to test the index view.
    '''
    @classmethod
    def setUpTestData(cls):
        cls.test_user = User.objects.create_user(username='TestUser', email='test@test.com',
                                                 password='tH1$isA7357')
        cls.test_user.save()

    def test_get_index(self):
        '''
        The index page should return 200 and use the index.html template.
        '''
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')

    def test_index_has_bugs_this_week(self):
        '''
        The index page should show the number of bugs with status set to done in the last 7 days.
        '''
        response = self.client.get('/')
        self.assertEqual(0, response.context['bugs_this_week'])

        for day in range(10):
            done_bug = Ticket.objects.create(user=self.test_user, title='Test ticket', content='Test ticket', ticket_type='Bug')
            done_bug.done = timezone.now() - timedelta(days=day, minutes=-30)
            done_bug.save()

        response = self.client.get('/')
        self.assertEqual(8, response.context['bugs_this_week'])

    def test_index_has_features_coming_soon(self):
        '''
        The index should show the number of features with stats set to doing.
        '''
        response = self.client.get('/')
        self.assertEqual(0, response.context['features_coming_soon'])

        for num in range(10):
            doing_feature = Ticket.objects.create(user=self.test_user, title='Test ticket', content='Test ticket', ticket_type='Feature')
            doing_feature.save()
            doing_feature.set_status('doing')

        response = self.client.get('/')
        self.assertEqual(10, response.context['features_coming_soon'])

    def test_index_has_total_features_implemented(self):
        '''
        The index should show the number of features with stats set to doing.
        '''
        response = self.client.get('/')
        self.assertEqual(0, response.context['total_features_implemented'])

        for num in range(100):
            doing_feature = Ticket.objects.create(user=self.test_user, title='Test ticket', content='Test ticket', ticket_type='Feature')
            doing_feature.save()
            doing_feature.set_status('done')

        response = self.client.get('/')
        self.assertEqual(100, response.context['total_features_implemented'])

    def test_index_has_most_requested_feature_url(self):
        popular_feature = Ticket.objects.create(user=self.test_user, title='Test ticket', content='Test ticket', ticket_type='Feature')
        popular_feature.save()
        popular_feature.set_status('approved')

        for num in range(10):
            vote = Vote.objects.create(user=self.test_user, ticket=popular_feature)
            vote.save()

        response = self.client.get('/')
        self.assertEqual(popular_feature.get_absolute_url(), response.context['most_requested_feature_url'])


class TestDateRangeMixin(TestCase):
    '''
    Class to test the date range mixin.
    '''
    @classmethod
    def setUpTestData(cls):
        test_user = User.objects.create_user(username='TestUser', email='test@test.com',
                                             password='tH1$isA7357')
        test_user.save()

        voting_user = User.objects.create_user(username='VotingUser', email='test@test.com',
                                               password='tH1$isA7357')
        voting_user.save()

        ticket = Ticket.objects.create(user=test_user, title='Test Ticket', content='Test ticket', ticket_type="Feature")

        for n in range(7):
            for i in range(n + 1):
                vote = Vote.objects.create(user=voting_user, ticket=ticket, count=n + 1)
                vote.created = timezone.make_aware(datetime(2019, 1, 1) + timedelta(days=n), timezone=timezone.get_current_timezone())
                vote.save()

    def setUp(self):
        self.factory = RequestFactory()
        self.view = DateRangeMixin()

    def test_get_form_kwargs_adds_form(self):
        '''
        The get_form_kwargs method should add the DateRangeForm to the view, and validates it.
        '''
        self.view.request = self.factory.get('/date-range/')
        self.view.get_form_kwargs()
        self.assertIsInstance(self.view.form, DateRangeForm)
        self.assertTrue(self.view.form.cleaned_data['start_date'])
        self.assertTrue(self.view.form.cleaned_data['end_date'])

    def test_get_form_kwargs_returns_default_dates(self):
        '''
        The get_form_kwargs should cause the added form to contain the defaults of start_date today - 1 week, and end_date today if no query string.
        '''
        self.view.request = self.factory.get('/date-range/')
        self.view.get_form_kwargs()
        self.assertEqual(date.today() - timedelta(days=7), self.view.form.cleaned_data['start_date'])
        self.assertTrue(date.today(), self.view.form.cleaned_data['end_date'])

    def test_get_form_kwargs_returns_query_dates(self):
        '''
        The get_fom_kwargs should cause the added form to contain the dates from the query string.
        '''
        self.view.request = self.factory.get('/date-range/?start_date=2019-01-01&end_date=2019-02-01')
        self.view.get_form_kwargs()
        self.assertEqual(date(2019, 1, 1), self.view.form.cleaned_data['start_date'])
        self.assertTrue(date(2019, 2, 1), self.view.form.cleaned_data['end_date'])

    def test_get_date_range_and_annotate_returns_list(self):
        '''
        The get_date_range_and_annotate method returns a list of dates and totals for that date range.
        '''
        self.view.request = self.factory.get('/date-range/?start_date=2019-01-01&end_date=2019-01-03')
        self.view.get_form_kwargs()
        results = self.view.get_date_range_and_annotate(Vote.objects.all())

        self.assertIn({'date': '2019-01-01', 'total': 1}, results)
        self.assertIn({'date': '2019-01-02', 'total': 2}, results)
        self.assertIn({'date': '2019-01-03', 'total': 3}, results)
        self.assertTrue(all(map(lambda result: result['date'] >= '2019-01-01' and result['date'] <= '2019-01-03', results)))

    def test_get_date_range_and_annotate_total_returns_list(self):
        '''
        The get_date_range_and_annotate method returns a list of dates and totals for that date range, with total calculated using the prescribed method.
        '''
        self.view.request = self.factory.get('/date-range/?start_date=2019-01-01&end_date=2019-01-03')
        self.view.get_form_kwargs()
        results = self.view.get_date_range_and_annotate(Vote.objects.all(), total=Sum('count'))

        self.assertIn({'date': '2019-01-01', 'total': 1}, results)
        self.assertIn({'date': '2019-01-02', 'total': 4}, results)
        self.assertIn({'date': '2019-01-03', 'total': 9}, results)

        results = self.view.get_date_range_and_annotate(Vote.objects.all(), total=Max('count'))

        self.assertIn({'date': '2019-01-01', 'total': 1}, results)
        self.assertIn({'date': '2019-01-02', 'total': 2}, results)
        self.assertIn({'date': '2019-01-03', 'total': 3}, results)

    def test_get_date_range_and_annotate_returns_empty_list(self):
        '''
        The get_date_range_and_annotate method returns an empty list if no records are found between the dates,
        or the date range form is invalid.
        '''

        self.view.request = self.factory.get('/date-range/?start_date=2019-02-01&end_date=2019-02-03')
        self.view.get_form_kwargs()
        results = self.view.get_date_range_and_annotate(Vote.objects.all())

        self.assertEqual([], results)

        self.view.request = self.factory.get('/date-range/?start_date=notadate&end_date=notadate')
        self.view.get_form_kwargs()
        results = self.view.get_date_range_and_annotate(Vote.objects.all())

        self.assertEqual([], results)

    def test_get_context_data_adds_date_range_form(self):
        '''
        The get_context_data method should return a dictionary containing a DateRangeForm as date_range_form,
        with initial values that match the query, or the defaults.
        '''
        self.view.request = self.factory.get('/date-range/')
        context = self.view.get_context_data()

        self.assertIsInstance(context['date_range_form'], DateRangeForm)
        self.assertEqual(date.today() - timedelta(days=7), context['date_range_form'].initial['start_date'])
        self.assertEqual(date.today(), context['date_range_form'].initial['end_date'])

        self.view.request = self.factory.get('/date-range/?start_date=2019-01-01&end_date=2019-01-03')
        context = self.view.get_context_data()

        self.assertEqual(date(2019, 1, 1), context['date_range_form'].initial['start_date'])
        self.assertEqual(date(2019, 1, 3), context['date_range_form'].initial['end_date'])

    def test_get_context_data_adds_date_range_for_this_week(self):
        '''
        The get_context_data method should return a dictionary containing a date_range of 'For This Week' for the default values.
        And 'Between d/m/y-d/m/y' for all other values.
        '''
        self.view.request = self.factory.get('/date-range/')
        context = self.view.get_context_data()

        self.assertEqual('For This Week', context['date_range'])

        self.view.request = self.factory.get('/date-range/?start_date=2019-01-01&end_date=2019-01-03')
        context = self.view.get_context_data()

        self.assertEqual('Between 01/01/19-03/01/19', context['date_range'])


class TestTicketStatsView(TestCase):
    '''
    Class to test individual ticket stats view.
    '''
    @classmethod
    def setUpTestData(cls):
        cls.test_user = User.objects.create_user(username='TestUser', email='test@test.com',
                                                 password='tH1$isA7357')
        cls.test_user.save()

        cls.other_user = User.objects.create_user(username='OtherUser', email='test@test.com',
                                                  password='tH1$isA7357')
        cls.other_user.save()

        cls.admin_user = User.objects.create_user(username='AdminUser', email='admin@test.com',
                                                  password='tH1$isA7357')
        cls.admin_user.save()
        cls.admin_user.user_permissions.add(Permission.objects.get(codename='can_view_all_stats'))

        cls.test_ticket = Ticket.objects.create(user=cls.test_user, title='Test ticket', content='Test ticket')

    def setUp(self):
        self.client.logout()

    def test_get_ticket_stats_view_only_acessible_to_author_or_admin(self):
        '''
        The ticket stats page should only be accessible to the author, or admin with can view all stats permission.
        Should use ticket_stats_detail.html
        '''
        response = self.client.get('/stats/{}/'.format(self.test_ticket.id))
        self.assertEqual(response.status_code, 403)

        self.client.login(username='OtherUser', password='tH1$isA7357')
        response = self.client.get('/stats/{}/'.format(self.test_ticket.id))
        self.assertEqual(response.status_code, 403)
        self.client.logout()

        self.client.login(username='TestUser', password='tH1$isA7357')
        response = self.client.get('/stats/{}/'.format(self.test_ticket.id))
        self.assertEqual(response.status_code, 200)
        self.client.logout()

        self.client.login(username='AdminUser', password='tH1$isA7357')
        response = self.client.get('/stats/{}/'.format(self.test_ticket.id))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ticket_stats_detail.html')

    def test_get_ticket_stats_context_contains_json_chart_data(self):
        '''
        The context should be passed a json object containing chart data for views, comments and votes.
        '''
        self.client.login(username='AdminUser', password='tH1$isA7357')
        response = self.client.get('/stats/{}/'.format(self.test_ticket.id))
        chart_data = json.loads(response.context['chart_data'])
        
        self.assertIn('comments', chart_data.keys())
        self.assertIn('views', chart_data.keys())
        self.assertIn('votes', chart_data.keys())


class TestAllTicketsStatsView(TestCase):
    '''
    Class to test all tickets stats view.
    '''
    @classmethod
    def setUpTestData(cls):
        cls.test_user = User.objects.create_user(username='TestUser', email='test@test.com',
                                                 password='tH1$isA7357')
        cls.test_user.save()

        cls.other_user = User.objects.create_user(username='OtherUser', email='test@test.com',
                                                  password='tH1$isA7357')
        cls.other_user.save()

        cls.admin_user = User.objects.create_user(username='AdminUser', email='admin@test.com',
                                                  password='tH1$isA7357')
        cls.admin_user.save()
        cls.admin_user.user_permissions.add(Permission.objects.get(codename='can_view_all_stats'))

    def setUp(self):
        self.client.logout()

    def test_get_all_tickets_stats_view_only_acessible_to_admin(self):
        '''
        The all tickets stats page should only be accessible to admins with can view all stats permission.
        Should use ticket_stats_all.html
        '''
        response = self.client.get('/stats/')
        self.assertEqual(response.status_code, 403)

        self.client.login(username='TestUser', password='tH1$isA7357')
        response = self.client.get('/stats/')
        self.assertEqual(response.status_code, 403)
        self.client.logout()

        self.client.login(username='AdminUser', password='tH1$isA7357')
        response = self.client.get('/stats/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ticket_stats_all.html')

    def test_get_all_tickets_stats_context_contains_json_chart_data(self):
        '''
        The context should be passed a json object containing chart data for bugs, features, views, comments and votes.
        '''
        self.client.login(username='AdminUser', password='tH1$isA7357')
        response = self.client.get('/stats/')
        chart_data = json.loads(response.context['chart_data'])

        self.assertIn('bugs', chart_data.keys())
        self.assertIn('features', chart_data.keys())
        self.assertIn('comments', chart_data.keys())
        self.assertIn('views', chart_data.keys())
        self.assertIn('votes', chart_data.keys())

    def test_get_all_tickets_stats_context_contains_total_awaiting_approval(self):
        '''
        The context should contain the total number of tickets awaiting approval.
        '''
        self.client.login(username='AdminUser', password='tH1$isA7357')
        response = self.client.get('/stats/')

        self.assertEqual(0, response.context['awaiting_approval'])

        for n in range(7):
            ticket = Ticket.objects.create(user=self.test_user, title='Test ticket', content='Test ticket', ticket_type='Feature')
            ticket.save()

        response = self.client.get('/stats/')

        self.assertEqual(7, response.context['awaiting_approval'])

    def test_get_all_tickets_stats_context_contains_top_5_features(self):
        '''
        The context should contain the top 5 features.
        '''
        for n in range(7):
            ticket = Ticket.objects.create(user=self.test_user, title='Test feature {}'.format(n), content='Test ticket', ticket_type='Feature')
            ticket.set_status('approved')
            ticket.save()
            for i in range(n):
                vote = Vote.objects.create(ticket=ticket, user=self.other_user)
                vote.save()

        self.client.login(username='AdminUser', password='tH1$isA7357')
        response = self.client.get('/stats/')

        self.assertEqual('Test feature 6', response.context['top_5_features'][0].title)
        self.assertEqual('Test feature 2', response.context['top_5_features'][4].title)

    def test_get_all_tickets_stats_context_contains_top_5_bugs(self):
        '''
        The context should contain the top 5 features.
        '''
        for n in range(7):
            ticket = Ticket.objects.create(user=self.test_user, title='Test bug {}'.format(n), content='Test ticket', ticket_type='Bug')
            ticket.set_status('approved')
            ticket.save()
            for i in range(n):
                vote = Vote.objects.create(ticket=ticket, user=self.other_user)
                vote.save()

        self.client.login(username='AdminUser', password='tH1$isA7357')
        response = self.client.get('/stats/')

        self.assertEqual('Test bug 6', response.context['top_5_bugs'][0].title)
        self.assertEqual('Test bug 2', response.context['top_5_bugs'][4].title)


class TestTransactionStatsView(TestCase):
    '''
    Class to test transaction stats view.
    '''
    @classmethod
    def setUpTestData(cls):
        cls.test_user = User.objects.create_user(username='TestUser', email='test@test.com',
                                                 password='tH1$isA7357')
        cls.test_user.save()

        cls.other_user = User.objects.create_user(username='OtherUser', email='test@test.com',
                                                  password='tH1$isA7357')
        cls.other_user.save()

        cls.admin_user = User.objects.create_user(username='AdminUser', email='admin@test.com',
                                                  password='tH1$isA7357')
        cls.admin_user.save()
        cls.admin_user.user_permissions.add(Permission.objects.get(codename='can_view_transactions_stats'))

    def setUp(self):
        self.client.logout()

    def test_get_transaction_stats_view_only_acessible_to_admin(self):
        '''
        The all tickets stats page should only be accessible to admins with can view all stats permission.
        Should use transactions_stats.html
        '''
        response = self.client.get('/stats/transactions/')
        self.assertEqual(response.status_code, 403)

        self.client.login(username='TestUser', password='tH1$isA7357')
        response = self.client.get('/stats/transactions/')
        self.assertEqual(response.status_code, 403)
        self.client.logout()

        self.client.login(username='AdminUser', password='tH1$isA7357')
        response = self.client.get('/stats/transactions/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'transaction_stats.html')

    def test_get_transaction_stats_context_contains_json_chart_data(self):
        '''
        The context should be passed a json object containing chart data for sales and refunds.
        '''
        self.client.login(username='AdminUser', password='tH1$isA7357')
        response = self.client.get('/stats/transactions/')
        chart_data = json.loads(response.context['chart_data'])

        self.assertIn('sales', chart_data.keys())
        self.assertIn('refunds', chart_data.keys())


class TestRoadmapView(TestCase):
    '''
    Class to test Roadmap View.
    '''
    @classmethod
    def setUpTestData(cls):
        test_user = User.objects.create_user(username='TestUser', email='test@test.com',
                                             password='tH1$isA7357')
        test_user.save()

        for n in range(7):
            coming_soon_ticket = Ticket.objects.create(user=test_user, title='Coming Soon {}'.format(n),
                                                       content='Test ticket', ticket_type='Feature' if n % 2 == 0 else 'Bug')
            coming_soon_ticket.set_status('doing')
            coming_soon_ticket.doing = timezone.now() - timedelta(days=7 - n)
            coming_soon_ticket.save()

        for n in range(25):
            completed_ticket = Ticket.objects.create(user=test_user, title='Completed {}'.format(n),
                                                     content='Test ticket', ticket_type='Feature' if n % 2 == 0 else 'Bug')
            completed_ticket.set_status('done')
            completed_ticket.done = timezone.now() - timedelta(days=25 - n)
            completed_ticket.save()

    def test_get_roadmap(self):
        '''
        The roadmap page should return 200 and use the roadmap.html template.
        '''
        response = self.client.get('/roadmap/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'roadmap.html')

    def test_get_contains_ticket_list(self):
        '''
        The roadmap page should contain a list of ticket details of length 10 or less. Ordered first by coming soon, then by done date.
        '''

        response = self.client.get('/roadmap/')
        ticket_list = response.context['tickets']
        self.assertLessEqual(10, len(ticket_list))
        for ticket in ticket_list:
            self.assertIn('title', ticket.keys())
            self.assertRegex(ticket['url'], '^/tickets/[0-9]+/$')
            self.assertRegex(ticket['type'], '^(Bug|Feature)$')
            self.assertRegex(ticket['date'], '^(Coming Soon|[0-9]{2}/[0-9]{2}/[0-9]{2})$')

        self.assertEqual([ticket['date'] for ticket in ticket_list[:7]], ['Coming Soon' for n in range(7)])

        self.assertGreater(datetime.strptime(ticket_list[7]['date'], '%d/%m/%y'), datetime.strptime(ticket_list[8]['date'], '%d/%m/%y'))
        self.assertGreater(datetime.strptime(ticket_list[8]['date'], '%d/%m/%y'), datetime.strptime(ticket_list[9]['date'], '%d/%m/%y'))

    def test_get_page_json_returns_ticket_list_and_done(self):
        '''
        Getting a page with request type as json should return a list of tickets ordered by date.
        '''
        factory = RequestFactory()
        request = factory.get('/roadmap/?page=1')
        request.content_type = 'application/json'

        response = RoadmapView.as_view()(request)
        response_data = json.loads(response.content.decode())
        ticket_list = response_data['tickets']
        self.assertFalse(response_data['done'])

        self.assertLessEqual(10, len(ticket_list))
        for ticket in ticket_list:
            self.assertIn('title', ticket.keys())
            self.assertRegex(ticket['url'], '^/tickets/[0-9]+/$')
            self.assertRegex(ticket['type'], '^(Bug|Feature)$')
            self.assertRegex(ticket['date'], '^(Coming Soon|[0-9]{2}/[0-9]{2}/[0-9]{2})$')

        self.assertGreater(datetime.strptime(ticket_list[0]['date'], '%d/%m/%y'), datetime.strptime(ticket_list[1]['date'], '%d/%m/%y'))
        self.assertGreater(datetime.strptime(ticket_list[2]['date'], '%d/%m/%y'), datetime.strptime(ticket_list[7]['date'], '%d/%m/%y'))

    def test_get_page_json_returns_done_after_last_page(self):
        '''
        Getting a page with request type as json should return a value for done of True for the final page or later.
        '''
        factory = RequestFactory()
        request = factory.get('/roadmap/?page=1')
        request.content_type = 'application/json'

        response = RoadmapView.as_view()(request)
        response_data = json.loads(response.content.decode())
        self.assertEqual(10, len(response_data['tickets']))
        self.assertFalse(response_data['done'])

        request = factory.get('/roadmap/?page=3')
        request.content_type = 'application/json'

        response = RoadmapView.as_view()(request)
        response_data = json.loads(response.content.decode())
        self.assertEqual(2, len(response_data['tickets']))
        self.assertTrue(response_data['done'])

        request = factory.get('/roadmap/?page=6')
        request.content_type = 'application/json'

        response = RoadmapView.as_view()(request)
        response_data = json.loads(response.content.decode())
        self.assertEqual(0, len(response_data['tickets']))
        self.assertTrue(response_data['done'])
