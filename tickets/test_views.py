from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User, Permission, AnonymousUser
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.messages import get_messages
from django.shortcuts import reverse
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta
from tickets.models import Ticket, Comment, Vote, Pageview
from tickets.forms import CommentForm, TicketForm, BugForm, FeatureForm, VoteForm, FilterForm
from tickets.views import AddTicketView


class TicketsTestCase(TestCase):
    '''
    Abstract class for testing tickets.
    '''

    @classmethod
    def setUpTestData(cls):
        cls.test_user = User.objects.create_user(username='TestUser', email='test@test.com',
                                                 password='tH1$isA7357')
        cls.test_user.save()

        cls.admin_user = User.objects.create_user(username='AdminUser', email='admin@test.com',
                                                  password='tH1$isA7357')
        cls.admin_user.save()

        cls.admin_user.user_permissions.set(Permission.objects.all())

        cls.other_user = User.objects.create_user(username='OtherUser', email='other@test.com',
                                                  password='tH1$isA7357')
        cls.other_user.save()

    def setUp(self):
        self.client.logout()


class TicketViewsTestCase(TicketsTestCase):
    '''
    Class to test Ticket views.
    '''

    @classmethod
    def setUpTestData(cls):
        super(TicketViewsTestCase, cls).setUpTestData()

        cls.test_ticket1 = Ticket(user=cls.test_user, title='Test title 1', content='Test content 1')
        cls.test_ticket1.save()
        cls.test_ticket1.set_status('approved')

        cls.test_ticket2 = Ticket(user=cls.test_user, title='Test title 2', content='Test content 2')
        cls.test_ticket2.save()

        cls.test_ticket3 = Ticket(user=cls.test_user, title='Test title 2', content='Test content 2')
        cls.test_ticket3.save()

# TICKET DETAIL VIEW TESTS #

    def test_get_ticket_detail(self):
        '''
        The ticket detail view should return 200 for approved tickets, and use the ticket_detail.html template.
        '''
        response = self.client.get('/tickets/1/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ticket_detail.html')

    def test_ticket_detail_contains_ticket(self):
        '''
        The ticket detail view should pass the ticket to the page context
        '''
        response = self.client.get('/tickets/1/')
        self.assertEqual(response.context['object'], Ticket.objects.get(pk=1))

    def test_ticket_detail_has_comment_form_if_logged_in(self):
        '''
        The ticket detail view should pass the comment form to the page context only if the
        user is logged in.
        '''
        response = self.client.get('/tickets/1/')
        self.assertIsNone(response.context.get('comment_form'))

        self.client.login(username='TestUser', password='tH1$isA7357')
        response = self.client.get('/tickets/1/')
        self.assertIsInstance(response.context['comment_form'], CommentForm)

    def test_ticket_detail_awaiting_approval_author_and_admins_only(self):
        '''
        The ticket detail view should return 403 forbidden to users that are not the author, or admin
        for unapproved tickets.
        '''
        response = self.client.get('/tickets/2/')
        self.assertEqual(response.status_code, 403)

        self.client.login(username='OtherUser', password='tH1$isA7357')
        response = self.client.get('/tickets/2/')
        self.assertEqual(response.status_code, 403)
        self.client.logout()

        self.client.login(username='TestUser', password='tH1$isA7357')
        response = self.client.get('/tickets/2/')
        self.assertEqual(response.status_code, 200)
        self.client.logout()

        self.client.login(username='AdminUser', password='tH1$isA7357')
        response = self.client.get('/tickets/2/')
        self.assertEqual(response.status_code, 200)

    def test_ticket_detail_doesnt_have_comment_form_if_awaiting_approval(self):
        '''
        The ticket detail view should not have the comment form in its context if the ticket is not approved.
        '''
        self.client.login(username='TestUser', password='tH1$isA7357')
        response = self.client.get('/tickets/2/')
        self.assertIsNone(response.context.get('comment_form'))

    def test_ticket_detail_features_include_vote_form(self):
        '''
        Feature request tickets include the vote form for registered users to spend credits to vote.
        '''
        test_ticket = Ticket(user=self.test_user, title='Test feature',
                             ticket_type='Feature', content='Test feature')
        test_ticket.save()
        test_ticket.set_status('approved')

        self.client.login(username='OtherUser', password='tH1$isA7357')
        response = self.client.get('/tickets/{}/'.format(test_ticket.id))
        self.assertIsInstance(response.context['vote_form'], VoteForm)

    def test_ticket_detail_bugs_dont_include_vote_form(self):
        '''
        Bug report tickets do not include the vote form.
        '''
        self.client.login(username='OtherUser', password='tH1$isA7357')
        response = self.client.get('/tickets/1/')
        self.assertIsNone(response.context.get('vote_form'))

# ADD TICKET TESTS #

    def test_get_add_ticket(self):
        '''
        The add ticket view should redirect to the login page for anonymous users, and
        return 200 for logged in users.
        '''
        factory = RequestFactory()
        request = factory.get('/tickets/add/')
        request.user = AnonymousUser()

        response = AddTicketView.as_view()(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('login') + '?next=/tickets/add/')

        request = factory.get('/tickets/add/')
        request.user = self.test_user

        response = AddTicketView.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_post_add_ticket_redirects_anonymous(self):
        factory = RequestFactory()
        request = factory.post('/tickets/add/', {'title': 'New Ticket', 'content': 'It\'s new!'})
        request.user = AnonymousUser()

        response = AddTicketView.as_view()(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('login') + '?next=/tickets/add/')

    def test_post_add_ticket_creates_ticket(self):
        '''
        Post requests to add ticket with valid input should create a new ticket, and redirect
        to that ticket's page.
        '''
        factory = RequestFactory()
        request = factory.post('/tickets/add/', {'title': 'New Ticket', 'ticket_type': 'Bug', 'content': 'It\'s new!'})
        request.user = self.test_user
        request.session = 'session'
        request._messages = FallbackStorage(request)

        response = AddTicketView.as_view()(request)
        self.assertTrue(Ticket.objects.get(title='New Ticket'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, Ticket.objects.get(title='New Ticket').get_absolute_url())


# TEST ADD BUG #

    def test_get_report_bug_contains_bug_form_uses_template(self):
        '''
        The add bug view should contain the BugForm in the page context for get requests.
        '''
        self.client.login(username='TestUser', password='tH1$isA7357')
        response = self.client.get('/tickets/report-bug/')
        self.assertIsInstance(response.context['form'], BugForm)
        self.assertTemplateUsed(response, 'add_bug.html')

# TEST ADD Feature #

    def test_get_request_feature_contains_feature_form_uses_template(self):
        '''
        The add bug view should contain the BugForm in the page context for get requests.
        '''
        self.client.login(username='TestUser', password='tH1$isA7357')
        response = self.client.get('/tickets/request-feature/')
        self.assertIsInstance(response.context['form'], FeatureForm)
        self.assertTemplateUsed(response, 'add_feature.html')

# EDIT TICKET TESTS #

    def test_get_edit_ticket(self):
        '''
        The add ticket view should return 403 for anyone who isn't the author or an admin, and
        render the edit_ticket.html template for authorised users.
        '''
        response = self.client.get('/tickets/1/edit/')
        self.assertEqual(response.status_code, 403)

        self.client.login(username='OtherUser', password='tH1$isA7357')
        response = self.client.get('/tickets/1/edit/')
        self.assertEqual(response.status_code, 403)
        self.client.logout()

        self.client.login(username='AdminUser', password='tH1$isA7357')
        response = self.client.get('/tickets/1/edit/')
        self.assertEqual(response.status_code, 200)
        self.client.logout()

        self.client.login(username='TestUser', password='tH1$isA7357')
        response = self.client.get('/tickets/1/edit/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_ticket.html')

    def test_get_edit_ticket_contains_form(self):
        '''
        The edit ticket view should contain the TicketForm in the page context for get requests.
        '''
        self.client.login(username='TestUser', password='tH1$isA7357')
        response = self.client.get('/tickets/1/edit/')
        self.assertIsInstance(response.context['form'], TicketForm)

    def test_post_edit_ticket_anonymous_forbidden(self):
        '''
        Post requests for unauthorised users should return 403.
        '''
        response = self.client.post('/tickets/1/edit/', {'title': 'Updated Ticket', 'ticket_type': 'Bug', 'content': 'It\'s updated!'})
        self.assertEqual(response.status_code, 403)

        self.client.login(username='OtherUser', password='tH1$isA7357')
        response = self.client.post('/tickets/1/edit/', {'title': 'Updated Ticket', 'ticket_type': 'Bug', 'content': 'It\'s updated!'})
        self.assertEqual(response.status_code, 403)

    def test_post_edit_ticket_updates_ticket(self):
        '''
        Post requests to edit ticket with valid input should update the ticket, set it's edited time to now,
        and redirect to that ticket's page.
        '''
        self.client.login(username='TestUser', password='tH1$isA7357')
        response = self.client.post('/tickets/1/edit/', {'title': 'Updated Ticket', 'ticket_type': 'Bug', 'content': 'It\'s updated!'})
        self.assertEqual(Ticket.objects.get(pk=1).title, 'Updated Ticket')
        self.assertEqual(Ticket.objects.get(pk=1).content, 'It\'s updated!')
        self.assertTrue(Ticket.objects.get(pk=1).edited)
        self.assertRedirects(response, Ticket.objects.get(pk=1).get_absolute_url())

# SET TICKET STATUS TESTS #

    def test_post_set_ticket_status(self):
        '''
        Only users with permissions can set ticket status, everyone else returns 403 forbidden.
        Authorised users are redirected to the ticket.
        '''
        response = self.client.post('/tickets/1/approved/')
        self.assertEqual(response.status_code, 403)
        self.client.logout()

        self.client.login(username='OtherUser', password='tH1$isA7357')
        response = self.client.post('/tickets/1/approved/')
        self.assertEqual(response.status_code, 403)
        self.client.logout()

        self.client.login(username='TestUser', password='tH1$isA7357')
        response = self.client.post('/tickets/1/approved/')
        self.assertEqual(response.status_code, 403)
        self.client.logout()

        self.client.login(username='AdminUser', password='tH1$isA7357')
        response = self.client.post('/tickets/1/approved/')
        self.assertRedirects(response, Ticket.objects.get(pk=1).get_absolute_url())

    def test_set_ticket_updates_ticket(self):
        '''
        The set status routes set the ticket to the corresponding status.
        '''
        self.client.login(username='AdminUser', password='tH1$isA7357')
        self.client.post('/tickets/1/approved/')
        self.assertEqual(Ticket.objects.get(pk=1).status, 'approved')

        self.client.post('/tickets/2/doing/')
        self.assertEqual(Ticket.objects.get(pk=2).status, 'doing')

        self.client.post('/tickets/3/done/')
        self.assertEqual(Ticket.objects.get(pk=3).status, 'done')

# VOTE FOR TICKET TESTS #

    def test_post_vote_for_ticket(self):
        '''
        The vote route should return 403 for anonymous users, and redirect to the
        ticket for everyone else.
        '''
        response = self.client.post('/tickets/1/vote/')
        self.assertEqual(response.status_code, 403)
        self.client.logout()

        self.client.login(username='TestUser', password='tH1$isA7357')
        response = self.client.post('/tickets/1/vote/')
        self.assertRedirects(response, Ticket.objects.get(pk=1).get_absolute_url())

    def test_vote_for_ticket_increases_no_votes(self):
        '''
        Voting for an ticket should increase it's vote count.
        '''
        initial_votes = Ticket.objects.get(pk=2).no_votes
        self.client.login(username='TestUser', password='tH1$isA7357')
        self.client.post('/tickets/2/vote/')
        self.assertGreater(Ticket.objects.get(pk=2).no_votes, initial_votes)

    def test_users_can_only_vote_for_bugs_once(self):
        '''
        Users can only vote for a bug once, voting again does not increase the count
        and sends the user a message to notify them.
        '''
        self.client.login(username='TestUser', password='tH1$isA7357')
        self.client.post('/tickets/3/vote/')
        initial_votes = Ticket.objects.get(pk=3).no_votes

        response = self.client.post('/tickets/3/vote/')
        self.assertEqual(initial_votes, Ticket.objects.get(pk=3).no_votes)
        self.assertIn('Already voted for bug fix.', map(str, get_messages(response.wsgi_request)))


class TicketListViewTestCase(TicketsTestCase):
    '''
    Class to test TicketListView.
    '''

    @classmethod
    def setUpTestData(cls):
        '''
        Prepare list of tickets to test filters against.
        '''
        super(TicketListViewTestCase, cls).setUpTestData()

        def create_test_tickets(count, user, ticket_type, status=None):
            '''
            Helper function to set up a list of tickets with the required ticket type and status.
            Adds comments, votes and pageviews, and muddles the timestamps up a bit.
            '''
            delay = timedelta(hours=1)

            for n in range(count):
                ticket = Ticket(user=user, title='Test title', ticket_type=ticket_type, content='Test content')
                ticket.save()
                ticket.created = timezone.now() - (delay * 2 * n)
                ticket.save()
                if status:
                    ticket.set_status(status)
                for i in range(n):
                    vote = Vote(user=cls.other_user, ticket=ticket)
                    vote.save()
                    pageview = Pageview(ticket=ticket)
                    pageview.save()
                    comment = Comment(user=cls.other_user, ticket=ticket, content='Test comment')
                    comment.save()

        # Create a variety of tickets to use in test querysets
        create_test_tickets(13, cls.test_user, 'Bug')
        create_test_tickets(12, cls.test_user, 'Feature')
        create_test_tickets(17, cls.test_user, 'Bug', 'approved')
        create_test_tickets(19, cls.test_user, 'Feature', 'approved')
        create_test_tickets(13, cls.test_user, 'Bug', 'doing')
        create_test_tickets(11, cls.test_user, 'Feature', 'doing')
        create_test_tickets(7, cls.test_user, 'Bug', 'done')
        create_test_tickets(4, cls.test_user, 'Feature', 'done')

        ticket = Ticket(user=cls.other_user, title='Test title', ticket_type='Bug', content='Test content')
        ticket.save()

    def assertOrderedBy(self, collection, attribute, desc=True):
        '''
        Helper function, to check a collection is ordered by an attribute.
        '''
        for i in range(len(collection) - 1):
            if desc:
                self.assertGreaterEqual(getattr(collection[i], attribute), getattr(collection[i + 1], attribute))
            else:
                self.assertLessEqual(getattr(collection[i], attribute), getattr(collection[i + 1], attribute))

    def test_get_tickets_list(self):
        '''
        The tickets list should return 200, and use the ticket_list.html template.
        '''
        response = self.client.get('/tickets/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ticket_list.html')

    def test_get_tickets_list_shows_approved_tickets(self):
        '''
        The tickets list page should contain approved tickets, the tickets first 10 should be
        passed to the page context.
        '''
        response = self.client.get('/tickets/')
        self.assertQuerysetEqual(response.context['object_list'], Ticket.objects.exclude(approved=None)[:10],
                                 transform=lambda x: x)

    def test_get_tickets_list_shows_all_tickets_for_admin(self):
        '''
        The tickets list page should contain the first 10 tickets, including those waiting approval for admin users.
        '''
        self.client.login(username='AdminUser', password='tH1$isA7357')
        response = self.client.get('/tickets/')
        self.assertQuerysetEqual(response.context['object_list'], Ticket.objects.all()[:10],
                                 transform=lambda x: x)

    def test_get_tickets_list_shows_unapproved_tickets_to_author(self):
        '''
        The tickets list page should contain the first 10 tickets, excluding those that are unapproved, except where they
        were authored by the current user.
        '''
        self.client.login(username='TestUser', password='tH1$isA7357')
        response = self.client.get('/tickets/')
        self.assertQuerysetEqual(response.context['object_list'], Ticket.objects.exclude(Q(approved=None) & ~Q(user=self.test_user))[:10],
                                 transform=lambda x: x)

    def test_get_tickets_list_includes_filter_form(self):
        '''
        The ticket list page context should include the filter form.
        '''
        response = self.client.get('/tickets/')
        self.assertIsInstance(response.context['filter_form'], FilterForm)

    def test_get_tickets_list_filters_by_ticket_type(self):
        '''
        Filtering by a particular ticket type should include only a list of that ticket type.
        '''
        response = self.client.get('/tickets/?ticket_type=Bug')
        self.assertQuerysetEqual(response.context['object_list'], Ticket.objects.exclude(approved=None).filter(ticket_type='Bug')[:10],
                                 transform=lambda x: x)

        response = self.client.get('/tickets/?ticket_type=Feature')
        self.assertQuerysetEqual(response.context['object_list'], Ticket.objects.exclude(approved=None).filter(ticket_type='Feature')[:10],
                                 transform=lambda x: x)

    def test_get_tickets_list_filters_by_status(self):
        '''
        Filtering by a particular status should include only a list of tickets with that status.
        '''
        response = self.client.get('/tickets/?status=approved')
        self.assertQuerysetEqual(response.context['object_list'], Ticket.objects.exclude(approved=None).filter(doing=None)[:10],
                                 transform=lambda x: x)

        response = self.client.get('/tickets/?status=doing')
        self.assertQuerysetEqual(response.context['object_list'], Ticket.objects.exclude(doing=None).filter(done=None)[:10],
                                 transform=lambda x: x)

        response = self.client.get('/tickets/?status=done')
        self.assertQuerysetEqual(response.context['object_list'], Ticket.objects.exclude(done=None)[:10],
                                 transform=lambda x: x)

        self.client.login(username='AdminUser', password='tH1$isA7357')
        response = self.client.get('/tickets/?status=awaiting')
        self.assertQuerysetEqual(response.context['object_list'], Ticket.objects.filter(approved=None)[:10],
                                 transform=lambda x: x)

    def test_get_tickets_list_order_by_oldest(self):
        '''
        Ordering results by oldest first should return the oldest tickets first.
        '''
        response = self.client.get('/tickets/?order_by=created')
        self.assertQuerysetEqual(response.context['object_list'], Ticket.objects.exclude(approved=None).order_by('created')[:10],
                                 transform=lambda x: x)

    def test_get_tickets_list_order_by_most_votes(self):
        '''
        Ordering results by most votes should return tickets with the most votes first.
        '''
        response = self.client.get('/tickets/?order_by=-votes')
        self.assertOrderedBy(response.context['object_list'], 'no_votes')

    def test_get_tickets_list_order_by_most_views(self):
        '''
        Ordering results by most views should return tickets with the most views first.
        '''
        response = self.client.get('/tickets/?order_by=-views')
        self.assertOrderedBy(response.context['object_list'], 'no_views')

    def test_get_tickets_list_order_by_most_comments(self):
        '''
        Ordering results by most comments should return tickets with the most comments first.
        '''
        response = self.client.get('/tickets/?order_by=-comment_count')
        self.assertOrderedBy(response.context['object_list'], 'no_comments')

    def test_get_tickets_list_no_tickets(self):
        '''
        The total number of tickets matching the current query should be added to the context.
        '''
        response = self.client.get('/tickets/')
        self.assertEqual(71, response.context['no_tickets'])

        response = self.client.get('/tickets/?ticket_type=Bug')
        self.assertEqual(37, response.context['no_tickets'])

        response = self.client.get('/tickets/?ticket_type=Feature')
        self.assertEqual(34, response.context['no_tickets'])

        response = self.client.get('/tickets/?ticket_type=Feature&status=done')
        self.assertEqual(4, response.context['no_tickets'])

    def test_get_tickets_list_pagination(self):
        '''
        The the ticket list page query arg should return the correct range of tickets in the query.
        '''
        response = self.client.get('/tickets/?page=2')
        self.assertQuerysetEqual(response.context['object_list'], Ticket.objects.exclude(approved=None)[10:20],
                                 transform=lambda x: x)

        response = self.client.get('/tickets/?ticket_type=Feature&page=3')
        self.assertQuerysetEqual(response.context['object_list'], Ticket.objects.exclude(approved=None).filter(ticket_type='Feature')[20:30],
                                 transform=lambda x: x)

        response = self.client.get('/tickets/?ticket_type=Feature&status=approved&page=2')
        self.assertQuerysetEqual(response.context['object_list'], Ticket.objects.exclude(approved=None).filter(ticket_type='Feature', doing=None)[10:19],
                                 transform=lambda x: x)

    def test_get_tickets_list_page_out_of_bounds_not_found(self):
        '''
        Pages beyond the range of results should return 404 not found.
        '''
        response = self.client.get('/tickets/?page=25')
        self.assertEqual(response.status_code, 404)

        response = self.client.get('/tickets/?ticket_type=Feature&status=approved&page=3')
        self.assertEqual(response.status_code, 404)

    def test_get_ticket_list_pagination_page_range(self):
        '''
        The page range for use in pagination should be up to 5 adjacent pages. Ideally +- 2 pages from the current one,
        or +4 from the first page, -4 from the last, or -1 +3 for the second page, or -3 +1 for the second last page.
        '''

        # Page one shows pagination for pages 1 through 5.
        response = self.client.get('/tickets/')
        self.assertEqual(range(1, 6), response.context['page_range'])

        # Page two and three also show pagination for pages 1 through 5.
        response = self.client.get('/tickets/?page=2')
        self.assertEqual(range(1, 6), response.context['page_range'])

        response = self.client.get('/tickets/?page=3')
        self.assertEqual(range(1, 6), response.context['page_range'])

        # Page five shows pagination for pages 3 through 7
        response = self.client.get('/tickets/?page=5')
        self.assertEqual(range(3, 8), response.context['page_range'])

        # Pages six through eight (the final page for this queryset) show pagination for pages 4 through 8.
        response = self.client.get('/tickets/?page=6')
        self.assertEqual(range(4, 9), response.context['page_range'])

        response = self.client.get('/tickets/?page=7')
        self.assertEqual(range(4, 9), response.context['page_range'])

        response = self.client.get('/tickets/?page=8')
        self.assertEqual(range(4, 9), response.context['page_range'])

    def test_tickets_list_query_string_contains_query(self):
        '''
        The query string should be added to the context for use in pagination to preserve the query
        and add the page number.
        '''
        response = self.client.get('/tickets/')
        self.assertEqual('?page=', response.context['query_string'])

        response = self.client.get('/tickets/?page=3')
        self.assertEqual('?page=', response.context['query_string'])

        response = self.client.get('/tickets/?ticket_type=Bug')
        self.assertEqual('?ticket_type=Bug&page=', response.context['query_string'])

        response = self.client.get('/tickets/?ticket_type=Bug&page=2')
        self.assertEqual('?ticket_type=Bug&page=', response.context['query_string'])

        response = self.client.get('/tickets/?order_by=-votes&ticket_type=Bug')
        self.assertEqual('?order_by=-votes&ticket_type=Bug&page=', response.context['query_string'])

        response = self.client.get('/tickets/?order_by=-votes&status=approved&ticket_type=Bug')
        self.assertEqual('?order_by=-votes&status=approved&ticket_type=Bug&page=', response.context['query_string'])


class CommentViewsTestCase(TestCase):
    '''
    Class to test Comment creation views.
    '''
    @classmethod
    def setUpTestData(cls):
        cls.test_user = User.objects.create_user(username='TestUser', email='test@test.com',
                                                 password='tH1$isA7357')
        cls.test_user.save()

        cls.admin_user = User.objects.create_user(username='AdminUser', email='admin@test.com',
                                                  password='tH1$isA7357')
        cls.admin_user.save()

        cls.admin_user.user_permissions.set(Permission.objects.all())

        cls.other_user = User.objects.create_user(username='OtherUser', email='other@test.com',
                                                  password='tH1$isA7357')
        cls.other_user.save()

        cls.test_ticket1 = Ticket(user=cls.test_user, title='Test title 1', content='Test content 1')
        cls.test_ticket1.save()

        cls.test_ticket2 = Ticket(user=cls.test_user, title='Test title 2', content='Test content 2')
        cls.test_ticket2.save()

    def setUp(self):
        self.client.logout()

    def test_get_add_comment(self):
        '''
        The add comment route should return 403 for anonymous users, and render the
        add_comment.html template for everyone else.
        '''
        response = self.client.get('/tickets/1/comments/add/')
        self.assertEqual(response.status_code, 403)

        self.client.login(username='TestUser', password='tH1$isA7357')
        response = self.client.get('/tickets/1/comments/add/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'add_comment.html')
        self.assertIsInstance(response.context['form'], CommentForm)

    def test_add_comment_non_existent_ticket_not_found(self):
        '''
        The add comment route should return 404 if the ticket doesn't exist.
        '''
        self.client.login(username='TestUser', password='tH1$isA7357')
        response = self.client.get('/tickets/999/comments/add/')
        self.assertEqual(response.status_code, 404)

    def test_post_add_comment(self):
        '''
        Post requests for add comment should create that comment and redirect to the ticket.
        '''
        self.client.login(username='TestUser', password='tH1$isA7357')
        response = self.client.post('/tickets/1/comments/add/', {'content': 'A test comment.'})
        self.assertTrue(Comment.objects.get(content='A test comment.'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, Comment.objects.get(content='A test comment.').get_absolute_url())

    def test_post_add_comment_to_non_existent_ticket_fails(self):
        '''
        Post requests for add comment for non existent tickets should fail.
        '''
        self.client.login(username='TestUser', password='tH1$isA7357')
        response = self.client.post('/tickets/999/comments/add/', {'content': 'This ticket never existed!'})
        self.assertFalse(Comment.objects.filter(content='This ticket never existed!'))
        self.assertEqual(response.status_code, 404)

    def test_get_post_add_comment_reply_to_non_existent_comment(self):
        '''
        The reply to comment route should return 404 if the parent comment is not found
        '''
        self.client.login(username='TestUser', password='tH1$isA7357')
        response = self.client.get('/tickets/2/comments/999/reply/')
        self.assertEqual(response.status_code, 404)
        response = self.client.post('/tickets/2/comments/999/reply/', {'content': 'Nothing to reply to!'})
        self.assertEqual(response.status_code, 404)

    def test_post_reply_add_comment_includes_parent(self):
        '''
        Post requests for add reply to comment should create that reply and redirect to the ticket.
        The reply should reference its parent.
        '''
        test_comment = Comment(user=self.other_user, ticket=self.test_ticket2, content='A test parent comment.')
        test_comment.save()
        test_comment = Comment.objects.get(content='A test parent comment.')

        self.client.login(username='TestUser', password='tH1$isA7357')
        response = self.client.post('/tickets/2/comments/{}/reply/'.format(test_comment.id),
                                    {'content': 'A test reply.'})
        self.assertTrue(Comment.objects.get(reply_to=test_comment))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, Comment.objects.get(reply_to=test_comment).get_absolute_url())
        self.assertEqual(Comment.objects.get(reply_to=test_comment).reply_to, test_comment)

    def test_get_post_reply_add_comment_to_mismatched_ticket_fails(self):
        '''
        Get and post requests for add reply to comment for non mismatched tickets should fail with a 400 bad request.
        '''
        test_comment = Comment(user=self.other_user, ticket=self.test_ticket2, content='A comment on ticket 2.')
        test_comment.save()
        test_comment = Comment.objects.get(content='A comment on ticket 2.')

        self.client.login(username='TestUser', password='tH1$isA7357')
        response = self.client.get('/tickets/1/comments/{}/reply/'.format(test_comment.id))
        self.assertEqual(response.status_code, 400)
        response = self.client.post('/tickets/1/comments/{}/reply/'.format(test_comment.id),
                                    {'content': 'A reply to the comment on ticket 2 for ticket 1.'})
        self.assertFalse(Comment.objects.filter(content='A reply to the comment on ticket 2 for ticket 1.'))
        self.assertEqual(response.status_code, 400)

    def test_get_post_reply_add_comment_reply_to_reply_fails(self):
        test_comment = Comment(user=self.other_user, ticket=self.test_ticket2, content='A primary comment on ticket 2.')
        test_comment.save()
        test_comment = Comment.objects.get(content='A primary comment on ticket 2.')
        test_reply = Comment(user=self.other_user, ticket=self.test_ticket2,
                             reply_to=test_comment, content='A reply to comment on ticket 2.')
        test_reply.save()
        test_reply = Comment.objects.get(content='A reply to comment on ticket 2.')

        self.client.login(username='TestUser', password='tH1$isA7357')
        response = self.client.get('/tickets/2/comments/{}/reply/'.format(test_reply.id))
        self.assertEqual(response.status_code, 400)
        response = self.client.post('/tickets/2/comments/{}/reply/'.format(test_reply.id),
                                    {'content': 'A reply to a reply.'})
        self.assertFalse(Comment.objects.filter(content='A reply to a reply.'))
        self.assertEqual(response.status_code, 400)

    def test_get_edit_comment(self):
        '''
        The edit comment view should return 403 for anyone who isn't the author or an admin, and
        render the edit_comment.html template for authorised users, and include the comment form.
        '''
        test_comment = Comment(user=self.test_user, ticket=self.test_ticket2, content='A comment by TestUser.')
        test_comment.save()
        test_comment = Comment.objects.get(content='A comment by TestUser.')

        response = self.client.get('/tickets/2/comments/{}/edit/'.format(test_comment.id))
        self.assertEqual(response.status_code, 403)

        self.client.login(username='OtherUser', password='tH1$isA7357')
        response = self.client.get('/tickets/2/comments/{}/edit/'.format(test_comment.id))
        self.assertEqual(response.status_code, 403)
        self.client.logout()

        self.client.login(username='AdminUser', password='tH1$isA7357')
        response = self.client.get('/tickets/2/comments/{}/edit/'.format(test_comment.id))
        self.assertEqual(response.status_code, 200)
        self.client.logout()

        self.client.login(username='TestUser', password='tH1$isA7357')
        response = self.client.get('/tickets/2/comments/{}/edit/'.format(test_comment.id))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_comment.html')
        self.assertIsInstance(response.context['form'], CommentForm)

    def test_post_edit_comment_anonymous_forbidden(self):
        '''
        Post requests for unauthorised users should return 403.
        '''
        test_comment = Comment(user=self.test_user, ticket=self.test_ticket2, content='Another comment by TestUser.')
        test_comment.save()
        test_comment = Comment.objects.get(content='Another comment by TestUser.')

        response = self.client.post('/tickets/2/comments/{}/edit/'.format(test_comment.id), {'content': 'It\'s edited!'})
        self.assertEqual(response.status_code, 403)

        self.client.login(username='OtherUser', password='tH1$isA7357')
        response = self.client.post('/tickets/2/comments/{}/edit/'.format(test_comment.id), {'content': 'It\'s edited!'})
        self.assertEqual(response.status_code, 403)

    def test_post_edit_comment_updates_comment(self):
        '''
        Post requests to edit comment with valid input should update the comment, set it's edited time to now,
        and redirect to that comment's page.
        '''
        test_comment = Comment(user=self.test_user, ticket=self.test_ticket2, content='A final comment by TestUser.')
        test_comment.save()
        test_comment = Comment.objects.get(content='A final comment by TestUser.')

        self.client.login(username='TestUser', password='tH1$isA7357')
        response = self.client.post('/tickets/2/comments/{}/edit/'.format(test_comment.id), {'content': 'Successfully edited!'})
        self.assertEqual(Comment.objects.get(pk=test_comment.id).content, 'Successfully edited!')
        self.assertTrue(Comment.objects.get(pk=test_comment.id).edited)
        self.assertRedirects(response, Comment.objects.get(pk=test_comment.id).get_absolute_url())
