from django.test import TestCase
from django.contrib.auth.models import User
from issues.models import Issue, Comment, Vote
from django.utils import timezone
from datetime import timedelta


class IssueModelTestCase(TestCase):
    '''
    Class to test the Issue model.
    '''
    @classmethod
    def setUpTestData(cls):
        cls.test_user = User.objects.create_user(username='TestUser', email='test@test.com',
                                                 password='tH1$isA7357')

        test_issue = Issue(user=cls.test_user, title='Test title', content='Test content')
        test_issue.save()

    def test_issue_str_is_issue_no_dash_title(self):
        '''
        Test the issue str name is of the format '{issue number} - {title}'
        '''
        issue = Issue.objects.get(id=1)
        self.assertEqual(str(issue), '1 - Test title')

    def test_absolute_url_returns_issue_detail(self):
        '''
        Test the absolute url returns an existing page, and that page uses
        the issue_detail template and holds the issue in its context.
        '''
        issue = Issue.objects.get(id=1)
        url = issue.get_absolute_url()
        response = self.client.get(str(url))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'issue_detail.html')
        self.assertEqual(response.context['object'], issue)

    def test_no_views_returns_correct_numbers(self):
        '''
        Test the no_views property returns the correct number of views.
        '''
        test_issue = Issue(user=self.test_user, title='Views', content='Test content')
        test_issue.save()

        test_issue = Issue.objects.get(id=test_issue.id)
        self.assertEqual(0, test_issue.no_views)

        self.client.get(str(test_issue.get_absolute_url()))
        test_issue = Issue.objects.get(id=test_issue.id)
        self.assertEqual(1, test_issue.no_views)

    def test_no_votes_returns_correct_numbers(self):
        '''
        Test the no_votes property returns the correct number of votes.
        '''
        test_issue = Issue(user=self.test_user, title='Votes', content='Test content')
        test_issue.save()

        for number in range(3):
            voter = User.objects.create_user(username='VoteUser{}'.format(number),
                                             email='test{}@test.com'.format(number),
                                             password='tH1$isA7357')
            vote = Vote(user=voter, issue=test_issue)
            vote.save()

        issue_zero_votes = Issue.objects.get(id=1)
        self.assertEqual(0, issue_zero_votes.no_votes)
        issue_three_votes = Issue.objects.get(id=test_issue.id)
        self.assertEqual(3, issue_three_votes.no_votes)

    def test_comments_returns_primary_comments(self):
        '''
        Test the comments property returns the Issue's comments, excluding replies
        (which are stored in the comments themselves).
        '''
        test_issue = Issue(user=self.test_user, title='Test Comments', content='Test content')
        test_issue.save()

        comment1 = Comment(user=self.test_user, issue=test_issue, content='Test comment 1')
        comment1.save()

        comment2 = Comment(user=self.test_user, issue=test_issue, content='Test comment 2')
        comment2.save()

        comment3 = Comment(user=self.test_user, issue=test_issue, content='Test comment 3')
        comment3.save()

        reply1 = Comment(user=self.test_user, issue=test_issue, reply_to=comment2, content='Test reply 3')
        reply1.save()

        test_issue = Issue.objects.get(id=test_issue.id)
        self.assertQuerysetEqual(test_issue.comments, Comment.objects.filter(issue=test_issue, reply_to=None),
                                 transform=lambda x: x, ordered=False)

    def test_no_comments_returns_total_comments(self):
        '''
        Test the no_comments property returns a count of all comments on an Issue.
        '''
        test_issue_comments = Issue(user=self.test_user, title='Test Comments', content='Test content')
        test_issue_comments.save()

        test_issue_wo_comments = Issue(user=self.test_user, title='Test Comments', content='Test content')
        test_issue_wo_comments.save()

        comment1 = Comment(user=self.test_user, issue=test_issue_comments, content='Test comment 1')
        comment1.save()

        comment2 = Comment(user=self.test_user, issue=test_issue_comments, content='Test comment 2')
        comment2.save()

        reply1 = Comment(user=self.test_user, issue=test_issue_comments, reply_to=comment2, content='Test comment 3')
        reply1.save()

        self.assertEqual(0, test_issue_wo_comments.no_comments)
        self.assertEqual(3, test_issue_comments.no_comments)

    def test_status_returns_most_recent_status(self):
        '''
        Test the status property returns the most advanced status that has been logged.
        '''
        test_issue = Issue(user=self.test_user, title='Status', content='Test content')
        test_issue.save()

        test_issue = Issue.objects.get(id=test_issue.id)
        self.assertEqual('awaiting approval', test_issue.status)

        test_issue.approved = timezone.now()
        test_issue.save()
        test_issue = Issue.objects.get(id=test_issue.id)
        self.assertEqual('approved', test_issue.status)

        test_issue.doing = timezone.now()
        test_issue.save()
        test_issue = Issue.objects.get(id=test_issue.id)
        self.assertEqual('doing', test_issue.status)

        test_issue.done = timezone.now()
        test_issue.save()
        test_issue = Issue.objects.get(id=test_issue.id)
        self.assertEqual('done', test_issue.status)

    def test_has_voted_returns_false_if_user_has_not_voted(self):
        '''
        Test that the has_voted method returns false if a user has not voted for the issue.
        '''
        test_issue = Issue.objects.get(id=1)
        self.assertFalse(test_issue.has_voted(self.test_user))

    def test_has_voted_returns_true_if_user_has_voted(self):
        '''
        Test that the has_voted method returns true if a user has voted for the issue.
        '''
        test_issue = Issue(user=self.test_user, title='Voting', content='Test content')
        test_issue.save()

        voter = User.objects.create_user(username='VotingUser', email='test@test.com',
                                         password='tH1$isA7357')

        vote = Vote(user=voter, issue=test_issue)
        vote.save()

        test_issue = Issue.objects.get(id=test_issue.id)
        self.assertTrue(test_issue.has_voted(voter))

    def test_set_status_changes_status(self):
        '''
        Test that the set_status method updates an Issue's status.
        '''
        test_issue = Issue(user=self.test_user, title='Set Status', content='Test content')
        test_issue.save()

        test_issue = Issue.objects.get(id=test_issue.id)
        self.assertEqual('awaiting approval', test_issue.status)

        test_issue.set_status('approved')
        test_issue = Issue.objects.get(id=test_issue.id)
        self.assertEqual('approved', test_issue.status)

        test_issue.set_status('doing')
        test_issue = Issue.objects.get(id=test_issue.id)
        self.assertEqual('doing', test_issue.status)

        test_issue.set_status('done')
        test_issue = Issue.objects.get(id=test_issue.id)
        self.assertEqual('done', test_issue.status)

    def test_set_status_sets_status_field_to_now(self):
        '''
        Test that the set_status method sets the apropriate field to the current time.
        '''
        test_issue = Issue(user=self.test_user, title='Set Status Time', content='Test content')
        test_issue.save()

        before = timezone.now()
        test_issue.set_status('doing')
        after = timezone.now()
        self.assertGreaterEqual(test_issue.doing, before)
        self.assertLessEqual(test_issue.doing, after)

    def test_set_status_returns_false_when_not_set(self):
        '''
        Test that the set_status method returns false when it hasn't updated the status.
        '''
        test_issue = Issue(user=self.test_user, title='Fail To Set Status', content='Test content')
        test_issue.save()

        test_issue.set_status('doing')
        self.assertFalse(test_issue.set_status('approved'))

    def test_set_status_sets_all_unset_previous_status_fields(self):
        '''
        Test that the set status method sets all previous unset status fields to the current time,
        but leaves set ones as they are.
        '''
        test_issue = Issue(user=self.test_user, title='Fail To Set Status', content='Test content')

        past_date = timezone.now() - timedelta(days=1)
        test_issue.approved = past_date
        test_issue.save()

        test_issue.set_status('done')

        test_issue = Issue.objects.get(id=test_issue.id)
        self.assertEqual(test_issue.approved, past_date)
        self.assertIsNotNone(test_issue.doing)
        self.assertIsNotNone(test_issue.done)


class CommentModelTestCase(TestCase):
    '''
    Class to test the Comment model.
    '''
    @classmethod
    def setUpTestData(cls):
        cls.test_user = User.objects.create_user(username='TestUser', email='test@test.com',
                                                 password='tH1$isA7357')

        cls.test_issue = Issue(user=cls.test_user, title='Test title', content='Test content')
        cls.test_issue.save()

        cls.comment1 = Comment(user=cls.test_user, issue=cls.test_issue, content='Test comment 1')
        cls.comment1.save()

        cls.comment2 = Comment(user=cls.test_user, issue=cls.test_issue, content='Test comment 2')
        cls.comment2.save()

        cls.reply1 = Comment(user=cls.test_user, issue=cls.test_issue, reply_to=cls.comment2, content='Test comment 3')
        cls.reply1.save()

    def test_comment_str_is_by_user_on_issue_no_at_dmy_hm(self):
        '''
        Test the str name is of the format 'by {User} on issue {Issue no.} @ DD/MM/YY HH:MM'
        '''
        comment = Comment.objects.get(id=self.comment1.id)
        self.assertRegex(str(comment), '^By TestUser on issue 1 \@ [0-9]{2}/[0-9]{2}/[0-9]{2} [0-9]{2}:[0-9]{2}$')

    def test_comment_url_returns_issue_and_comment_id(self):
        '''
        Test the absolute url points to the issue page, and the comment's element ID on that page.
        '''
        comment = Comment.objects.get(id=self.comment1.id)
        self.assertEqual(comment.get_absolute_url(), comment.issue.get_absolute_url() + '#comment-{}'.format(self.comment1.id))

    def test_comment_replies_contains_replies(self):
        '''
        Test replies property returns a comments replies.
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
