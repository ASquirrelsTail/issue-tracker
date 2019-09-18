from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from tickets.models import Ticket, Comment, Vote
from credits.models import Wallet


class TicketModelTestCase(TestCase):
    '''
    Class to test the Ticket model.
    '''
    @classmethod
    def setUpTestData(cls):
        cls.test_user = User.objects.create_user(username='TestUser', email='test@test.com',
                                                 password='tH1$isA7357')

        cls.bug_ticket = Ticket(user=cls.test_user, title='Test Bug', ticket_type='Bug', content='Test content')
        cls.bug_ticket.save()
        cls.bug_ticket.set_status('approved')

        cls.feature_ticket = Ticket(user=cls.test_user, title='Test Feature', ticket_type='Feature', content='Test content')
        cls.feature_ticket.save()
        cls.feature_ticket.set_status('approved')

# TEST TICKET PROPERTIES #

    def test_ticket_str_is_ticket_no_dash_title_dash_type(self):
        '''
        Test the ticket str name is of the format '{ticket number} - {title} - {ticket type}'
        '''
        ticket = Ticket.objects.get(id=self.bug_ticket.id)
        self.assertEqual(str(ticket), '1 - Test Bug - Bug Report')

        ticket = Ticket.objects.get(id=self.feature_ticket.id)
        self.assertEqual(str(ticket), '2 - Test Feature - Feature Request')

    def test_absolute_url_returns_ticket_detail(self):
        '''
        Test the absolute url returns an existing page, and that page uses
        the ticket_detail template and holds the ticket in its context.
        '''
        ticket = Ticket.objects.get(id=self.bug_ticket.id)
        url = ticket.get_absolute_url()
        response = self.client.get(str(url))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ticket_detail.html')
        self.assertEqual(response.context['object'], ticket)

    def test_noun_returns_verbose_ticket_type(self):
        ticket = Ticket.objects.get(id=self.bug_ticket.id)
        self.assertEqual(ticket.noun, 'Bug Report')

        feature_ticket = Ticket.objects.get(id=self.feature_ticket.id)
        self.assertEqual(feature_ticket.noun, 'Feature Request')

    def test_no_views_returns_correct_numbers(self):
        '''
        Test the no_views property returns the correct number of views.
        '''
        test_ticket = Ticket(user=self.test_user, title='Views', content='Test content')
        test_ticket.save()

        test_ticket = Ticket.objects.get(id=test_ticket.id)
        self.assertEqual(0, test_ticket.no_views)

        self.client.get(str(test_ticket.get_absolute_url()))
        test_ticket = Ticket.objects.get(id=test_ticket.id)
        self.assertEqual(1, test_ticket.no_views)

    def test_no_votes_returns_correct_numbers(self):
        '''
        Test the no_votes property returns the correct number of votes.
        '''
        test_ticket_bug = Ticket(user=self.test_user, title='Bug Votes', content='Test content')
        test_ticket_bug.save()

        test_ticket_feature = Ticket(user=self.test_user, title='Feature Votes', content='Test content')
        test_ticket_feature.save()

        for number in range(3):
            voter = User.objects.create_user(username='VoteUser{}'.format(number),
                                             email='test{}@test.com'.format(number),
                                             password='tH1$isA7357')
            bug_vote = Vote(user=voter, ticket=test_ticket_bug)
            bug_vote.save()
            feature_vote = Vote(user=voter, ticket=test_ticket_feature, count=3)
            feature_vote.save()

        ticket_zero_votes = Ticket.objects.get(id=self.bug_ticket.id)
        self.assertEqual(0, ticket_zero_votes.no_votes)
        ticket_three_votes = Ticket.objects.get(id=test_ticket_bug.id)
        self.assertEqual(3, ticket_three_votes.no_votes)
        ticket_nine_votes = Ticket.objects.get(id=test_ticket_feature.id)
        self.assertEqual(9, ticket_nine_votes.no_votes)

    def test_comments_returns_primary_comments(self):
        '''
        Test the comments property returns the Ticket's comments, excluding replies
        (which are stored in the comments themselves).
        '''
        test_ticket = Ticket(user=self.test_user, title='Test Comments', content='Test content')
        test_ticket.save()

        comment1 = Comment(user=self.test_user, ticket=test_ticket, content='Test comment 1')
        comment1.save()

        comment2 = Comment(user=self.test_user, ticket=test_ticket, content='Test comment 2')
        comment2.save()

        comment3 = Comment(user=self.test_user, ticket=test_ticket, content='Test comment 3')
        comment3.save()

        reply1 = Comment(user=self.test_user, ticket=test_ticket, reply_to=comment2, content='Test reply 3')
        reply1.save()

        test_ticket = Ticket.objects.get(id=test_ticket.id)
        self.assertQuerysetEqual(test_ticket.comments, Comment.objects.filter(ticket=test_ticket, reply_to=None),
                                 transform=lambda x: x, ordered=False)

    def test_no_comments_returns_total_comments(self):
        '''
        Test the no_comments property returns a count of all comments on an Ticket.
        '''
        test_ticket_comments = Ticket(user=self.test_user, title='Test Comments', content='Test content')
        test_ticket_comments.save()

        test_ticket_wo_comments = Ticket(user=self.test_user, title='Test Comments', content='Test content')
        test_ticket_wo_comments.save()

        comment1 = Comment(user=self.test_user, ticket=test_ticket_comments, content='Test comment 1')
        comment1.save()

        comment2 = Comment(user=self.test_user, ticket=test_ticket_comments, content='Test comment 2')
        comment2.save()

        reply1 = Comment(user=self.test_user, ticket=test_ticket_comments, reply_to=comment2, content='Test comment 3')
        reply1.save()

        self.assertEqual(0, test_ticket_wo_comments.no_comments)
        self.assertEqual(3, test_ticket_comments.no_comments)

    def test_status_returns_most_recent_status(self):
        '''
        Test the status property returns the most advanced status that has been logged.
        '''
        test_ticket = Ticket(user=self.test_user, title='Status', content='Test content')
        test_ticket.save()

        test_ticket = Ticket.objects.get(id=test_ticket.id)
        self.assertEqual('awaiting approval', test_ticket.status)

        test_ticket.approved = timezone.now()
        test_ticket.save()
        test_ticket = Ticket.objects.get(id=test_ticket.id)
        self.assertEqual('approved', test_ticket.status)

        test_ticket.doing = timezone.now()
        test_ticket.save()
        test_ticket = Ticket.objects.get(id=test_ticket.id)
        self.assertEqual('doing', test_ticket.status)

        test_ticket.done = timezone.now()
        test_ticket.save()
        test_ticket = Ticket.objects.get(id=test_ticket.id)
        self.assertEqual('done', test_ticket.status)

# TEST TICKET HAS_VOTED METHOD#

    def test_has_voted_returns_false_if_user_has_not_voted(self):
        '''
        Test that the has_voted method returns false if a user has not voted for the ticket.
        '''
        test_ticket = Ticket.objects.get(id=1)
        self.assertFalse(test_ticket.has_voted(self.test_user))

    def test_has_voted_returns_true_if_user_has_voted(self):
        '''
        Test that the has_voted method returns true if a user has voted for the ticket.
        '''
        test_ticket = Ticket(user=self.test_user, title='Voting', content='Test content')
        test_ticket.save()

        voter = User.objects.create_user(username='VotingUser', email='test@test.com',
                                         password='tH1$isA7357')

        vote = Vote(user=voter, ticket=test_ticket)
        vote.save()

        test_ticket = Ticket.objects.get(id=test_ticket.id)
        self.assertTrue(test_ticket.has_voted(voter))

# TEST TICKET VOTE METHOD FOR BUG TICKET TYPE #

    def test_vote_for_bug_increases_votes(self):
        '''
        Test that the vote method increases votes on bug type tickets.
        '''
        test_ticket = Ticket(user=self.test_user, title='Voting', ticket_type='Bug', content='Test content')
        test_ticket.save()

        voter = User.objects.create_user(username='VotingUser', email='test@test.com',
                                         password='tH1$isA7357')

        test_ticket.vote(voter)
        test_ticket = Ticket.objects.get(id=test_ticket.id)
        self.assertEqual(1, test_ticket.no_votes)

    def test_vote_for_bug_returns_success_and_message(self):
        '''
        Test that voting for a bug returns success as True, and an appropriate message.
        '''
        test_ticket = Ticket(user=self.test_user, title='Voting', ticket_type='Bug', content='Test content')
        test_ticket.save()

        voter = User.objects.create_user(username='VotingUser', email='test@test.com',
                                         password='tH1$isA7357')

        result = test_ticket.vote(voter)
        self.assertTrue(result['success'])
        self.assertIn('success', result['message'].lower())

    def test_vote_for_bug_twice_does_not_increase_votes_a_second_time(self):
        '''
        Test voting for a bug a second time does not increase the number of votes.
        '''
        test_ticket = Ticket(user=self.test_user, title='Voting', ticket_type='Bug', content='Test content')
        test_ticket.save()

        voter = User.objects.create_user(username='VotingUser', email='test@test.com',
                                         password='tH1$isA7357')

        test_ticket.vote(voter)
        test_ticket.vote(voter)
        test_ticket = Ticket.objects.get(id=test_ticket.id)
        self.assertEqual(1, test_ticket.no_votes)

    def test_vote_for_bug_twice_returns_failiure_and_message(self):
        '''
        Test that voting for a bug a second time returns success as False, and an appropriate message.
        '''
        test_ticket = Ticket(user=self.test_user, title='Voting', ticket_type='Bug', content='Test content')
        test_ticket.save()

        voter = User.objects.create_user(username='VotingUser', email='test@test.com',
                                         password='tH1$isA7357')

        test_ticket.vote(voter)
        result = test_ticket.vote(voter)
        self.assertFalse(result['success'])
        self.assertIn('already voted', result['message'].lower())

# TEST TICKET VOTE METHOD FOR FEATURE TICKET TYPE #

    def test_vote_for_feature_increases_votes_by_credits_spent(self):
        '''
        Test that the vote method increases votes on feature type tickets by the number of credits spent.
        '''
        test_ticket = Ticket(user=self.test_user, title='Voting', ticket_type='Feature', content='Test content')
        test_ticket.save()

        voter = User.objects.create_user(username='VotingUser', email='test@test.com',
                                         password='tH1$isA7357')
        wallet = Wallet(user=voter)
        wallet.save()
        wallet.credit(10)

        test_ticket.vote(voter, 5)
        test_ticket = Ticket.objects.get(id=test_ticket.id)
        self.assertEqual(5, test_ticket.no_votes)

    def test_vote_for_feature_returns_success_and_message(self):
        '''
        Test that voting for a feature returns success as True, and an appropriate message.
        '''
        test_ticket = Ticket(user=self.test_user, title='Voting', ticket_type='Feature', content='Test content')
        test_ticket.save()

        voter = User.objects.create_user(username='VotingUser', email='test@test.com',
                                         password='tH1$isA7357')
        wallet = Wallet(user=voter)
        wallet.save()
        wallet.credit(10)

        result = test_ticket.vote(voter, 5)
        self.assertTrue(result['success'])
        self.assertIn('success', result['message'].lower())

    def test_vote_for_feature_reduces_wallet_balance_by_credits_spent(self):
        '''
        Test that voting for a feature debits the user the correct number of credits.
        '''
        test_ticket = Ticket(user=self.test_user, title='Voting', ticket_type='Feature', content='Test content')
        test_ticket.save()

        voter = User.objects.create_user(username='VotingUser', email='test@test.com',
                                         password='tH1$isA7357')
        wallet = Wallet(user=voter)
        wallet.save()
        wallet.credit(10)

        test_ticket.vote(voter, 5)
        voter_wallet = Wallet.objects.get(id=wallet.id)
        self.assertEqual(5, voter_wallet.balance)

    def test_vote_for_feature_twice_increase_votes_a_second_time(self):
        '''
        Test voting for a feature a second time again increase the number of votes by the number of crdits spent.
        '''
        test_ticket = Ticket(user=self.test_user, title='Voting', ticket_type='Feature', content='Test content')
        test_ticket.save()

        voter = User.objects.create_user(username='VotingUser', email='test@test.com',
                                         password='tH1$isA7357')
        wallet = Wallet(user=voter)
        wallet.save()
        wallet.credit(10)

        test_ticket.vote(voter, 5)
        test_ticket.vote(voter, 3)
        test_ticket = Ticket.objects.get(id=test_ticket.id)
        self.assertEqual(8, test_ticket.no_votes)

    def test_vote_for_feature_no_credits_returns_failiure_and_message(self):
        '''
        Test that voting for a feature with an empty of non-existent wallet returns success as False,
        and an appropriate message.
        '''
        test_ticket = Ticket(user=self.test_user, title='Voting', ticket_type='Feature', content='Test content')
        test_ticket.save()

        voter = User.objects.create_user(username='VotingUser', email='test@test.com',
                                         password='tH1$isA7357')

        result = test_ticket.vote(voter, 5)
        self.assertFalse(result['success'])
        self.assertIn('insufficient credits', result['message'].lower())

        wallet = Wallet(user=voter)
        wallet.save()

        result = test_ticket.vote(voter, 5)
        self.assertFalse(result['success'])
        self.assertIn('insufficient credits', result['message'].lower())

    def test_vote_for_feature_insufficient_credits_returns_failiure_and_message(self):
        '''
        Test that voting for a feature with an empty of non-existent wallet returns success as False,
        and an appropriate message.
        '''
        test_ticket = Ticket(user=self.test_user, title='Voting', ticket_type='Feature', content='Test content')
        test_ticket.save()

        voter = User.objects.create_user(username='VotingUser', email='test@test.com',
                                         password='tH1$isA7357')

        wallet = Wallet(user=voter)
        wallet.save()
        wallet.credit(10)

        result = test_ticket.vote(voter, 15)
        self.assertFalse(result['success'])
        self.assertIn('insufficient credits', result['message'].lower())

# TEST TICKET SET_STATUS METHOD #

    def test_set_status_changes_status(self):
        '''
        Test that the set_status method updates an Ticket's status.
        '''
        test_ticket = Ticket(user=self.test_user, title='Set Status', content='Test content')
        test_ticket.save()

        test_ticket = Ticket.objects.get(id=test_ticket.id)
        self.assertEqual('awaiting approval', test_ticket.status)

        test_ticket.set_status('approved')
        test_ticket = Ticket.objects.get(id=test_ticket.id)
        self.assertEqual('approved', test_ticket.status)

        test_ticket.set_status('doing')
        test_ticket = Ticket.objects.get(id=test_ticket.id)
        self.assertEqual('doing', test_ticket.status)

        test_ticket.set_status('done')
        test_ticket = Ticket.objects.get(id=test_ticket.id)
        self.assertEqual('done', test_ticket.status)

    def test_set_status_sets_status_field_to_now(self):
        '''
        Test that the set_status method sets the apropriate field to the current time.
        '''
        test_ticket = Ticket(user=self.test_user, title='Set Status Time', content='Test content')
        test_ticket.save()

        before = timezone.now()
        test_ticket.set_status('doing')
        after = timezone.now()
        self.assertGreaterEqual(test_ticket.doing, before)
        self.assertLessEqual(test_ticket.doing, after)

    def test_set_status_returns_false_when_not_set(self):
        '''
        Test that the set_status method returns false when it hasn't updated the status.
        '''
        test_ticket = Ticket(user=self.test_user, title='Fail To Set Status', content='Test content')
        test_ticket.save()

        test_ticket.set_status('doing')
        self.assertFalse(test_ticket.set_status('approved'))

    def test_set_status_sets_all_unset_previous_status_fields(self):
        '''
        Test that the set status method sets all previous unset status fields to the current time,
        but leaves set ones as they are.
        '''
        test_ticket = Ticket(user=self.test_user, title='Fail To Set Status', content='Test content')

        past_date = timezone.now() - timedelta(days=1)
        test_ticket.approved = past_date
        test_ticket.save()

        test_ticket.set_status('done')

        test_ticket = Ticket.objects.get(id=test_ticket.id)
        self.assertEqual(test_ticket.approved, past_date)
        self.assertIsNotNone(test_ticket.doing)
        self.assertIsNotNone(test_ticket.done)


class CommentModelTestCase(TestCase):
    '''
    Class to test the Comment model.
    '''
    @classmethod
    def setUpTestData(cls):
        cls.test_user = User.objects.create_user(username='TestUser', email='test@test.com',
                                                 password='tH1$isA7357')

        cls.test_ticket = Ticket(user=cls.test_user, title='Test title', content='Test content')
        cls.test_ticket.save()

        cls.comment1 = Comment(user=cls.test_user, ticket=cls.test_ticket, content='Test comment 1')
        cls.comment1.save()

        cls.comment2 = Comment(user=cls.test_user, ticket=cls.test_ticket, content='Test comment 2')
        cls.comment2.save()

        cls.reply1 = Comment(user=cls.test_user, ticket=cls.test_ticket, reply_to=cls.comment2, content='Test comment 3')
        cls.reply1.save()

    def test_comment_str_is_by_user_on_ticket_no_at_dmy_hm(self):
        '''
        Test the str name is of the format 'by {User} on ticket {Ticket no.} @ DD/MM/YY HH:MM'
        '''
        comment = Comment.objects.get(id=self.comment1.id)
        self.assertRegex(str(comment), '^By TestUser on ticket 1 \@ [0-9]{2}/[0-9]{2}/[0-9]{2} [0-9]{2}:[0-9]{2}$')

    def test_comment_url_returns_ticket_and_comment_id(self):
        '''
        Test the absolute url points to the ticket page, and the comment's element ID on that page.
        '''
        comment = Comment.objects.get(id=self.comment1.id)
        self.assertEqual(comment.get_absolute_url(), comment.ticket.get_absolute_url() + '#comment-{}'.format(self.comment1.id))

    def test_comment_replies_contains_replies(self):
        '''
        Test replies property returns a comment's replies.
        '''
        comment = Comment.objects.get(id=self.comment2.id)
        self.assertIn(self.reply1, comment.replies)
        self.assertQuerysetEqual(comment.replies, Comment.objects.filter(reply_to=comment),
                                 transform=lambda x: x, ordered=False)

    def test_comment_no_replies_returns_no_replies(self):
        '''
        Test the no_replies property returns the number of replies.
        '''
        comment1 = Comment.objects.get(id=self.comment1.id)
        self.assertEqual(comment1.no_replies, 0)

        comment2 = Comment.objects.get(id=self.comment2.id)
        self.assertEqual(comment2.no_replies, 1)
