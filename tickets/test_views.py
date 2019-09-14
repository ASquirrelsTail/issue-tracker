from django.test import TestCase
from django.contrib.auth.models import User, Permission
from django.shortcuts import reverse
from tickets.models import Ticket, Comment
from tickets.forms import CommentForm, TicketForm


class TicketViewsTestCase(TestCase):
    '''
    Class to test Ticket views.
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

        cls.test_ticket3 = Ticket(user=cls.test_user, title='Test title 2', content='Test content 2')
        cls.test_ticket3.save()

    def setUp(self):
        self.client.logout()

# TICKET LIST TESTS #

    def test_get_tickets_list(self):
        '''
        The tickets list should return 200, and use the ticket_list.html template.
        '''
        response = self.client.get('/tickets/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ticket_list.html')

    def test_get_tickets_list_shows_tickets(self):
        '''
        The tickets list page should contain names of tickets, the tickets should be
        passed to the page context.
        '''
        response = self.client.get('/tickets/')
        self.assertQuerysetEqual(response.context['object_list'], Ticket.objects.all(),
                                 transform=lambda x: x, ordered=False)

# TICKET DETAIL VIEW TESTS #

    def test_get_ticket_detail(self):
        '''
        The ticket detail view should return 200, and use the ticket_detail.html yemplate
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

# ADD TICKET TESTS #

    def test_get_add_ticket(self):
        '''
        The add ticket view should redirect to the login page for anonymous users, and
        render the add_ticket.html for logged in users.
        '''
        response = self.client.get('/tickets/add/')
        self.assertRedirects(response, reverse('login') + '?next=/tickets/add/')

        self.client.login(username='TestUser', password='tH1$isA7357')
        response = self.client.get('/tickets/add/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'add_ticket.html')

    def test_get_add_ticket_contains_form(self):
        '''
        The add ticket view should contain the TicketForm in the page context for get requests.
        '''
        self.client.login(username='TestUser', password='tH1$isA7357')
        response = self.client.get('/tickets/add/')
        self.assertIsInstance(response.context['form'], TicketForm)

    def test_post_add_ticket_redirects_anonymous(self):
        response = self.client.post('/tickets/add/', {'title': 'New Ticket', 'content': 'It\'s new!'})
        self.assertRedirects(response, reverse('login') + '?next=/tickets/add/')

    def test_post_add_ticket_creates_ticket(self):
        '''
        Post requests to add ticket with valid input should create a new ticket, and redirect
        to that ticket's page.
        '''
        self.client.login(username='TestUser', password='tH1$isA7357')
        response = self.client.post('/tickets/add/', {'title': 'New Ticket', 'content': 'It\'s new!'})
        self.assertTrue(Ticket.objects.get(title='New Ticket'))
        self.assertRedirects(response, Ticket.objects.get(title='New Ticket').get_absolute_url())

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
        response = self.client.post('/tickets/1/edit/', {'title': 'Updated Ticket', 'content': 'It\'s updated!'})
        self.assertEqual(response.status_code, 403)

        self.client.login(username='OtherUser', password='tH1$isA7357')
        response = self.client.post('/tickets/1/edit/', {'title': 'Updated Ticket', 'content': 'It\'s updated!'})
        self.assertEqual(response.status_code, 403)

    def test_post_edit_ticket_updates_ticket(self):
        '''
        Post requests to edit ticket with valid input should update the ticket, set it's edited time to now,
        and redirect to that ticket's page.
        '''
        self.client.login(username='TestUser', password='tH1$isA7357')
        response = self.client.post('/tickets/1/edit/', {'title': 'Updated Ticket', 'content': 'It\'s updated!'})
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

    def test_users_can_only_vote_once(self):
        '''
        Users can only vote for an ticket once, voting again returns a 403 forbidden
        and does not increase the count.
        '''
        self.client.login(username='TestUser', password='tH1$isA7357')
        self.client.post('/tickets/3/vote/')
        initial_votes = Ticket.objects.get(pk=3).no_votes

        response = self.client.post('/tickets/3/vote/')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(initial_votes, Ticket.objects.get(pk=3).no_votes)


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
