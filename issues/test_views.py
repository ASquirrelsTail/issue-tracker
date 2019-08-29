from django.test import TestCase
from django.contrib.auth.models import User, Permission
from django.shortcuts import reverse
from issues.models import Issue, Comment
from issues.forms import CommentForm, IssueForm


class IssueViewsTestCase(TestCase):
    '''
    Class to test Issue views.
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

        cls.test_issue1 = Issue(user=cls.test_user, title='Test title 1', content='Test content 1')
        cls.test_issue1.save()

        cls.test_issue2 = Issue(user=cls.test_user, title='Test title 2', content='Test content 2')
        cls.test_issue2.save()

        cls.test_issue3 = Issue(user=cls.test_user, title='Test title 2', content='Test content 2')
        cls.test_issue3.save()

    def setUp(self):
        self.client.logout()

# ISSUE LIST TESTS #

    def test_get_issues_list(self):
        '''
        The issues list should return 200, and use the issue_list.html template.
        '''
        response = self.client.get('/issues/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'issue_list.html')

    def test_get_issues_list_shows_issues(self):
        '''
        The issues list page should contain names of issues, the issues should be
        passed to the page context.
        '''
        response = self.client.get('/issues/')
        self.assertQuerysetEqual(response.context['object_list'], Issue.objects.all(),
                                 transform=lambda x: x, ordered=False)

# ADD ISSUE TESTS #

    def test_get_add_issue(self):
        '''
        The add issue view should redirect to the login page for anonymous users, and
        render the add_issue.html for logged in users.
        '''
        response = self.client.get('/issues/add/')
        self.assertRedirects(response, reverse('login') + '?next=/issues/add/')

        self.client.login(username='TestUser', password='tH1$isA7357')
        response = self.client.get('/issues/add/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'add_issue.html')

    def test_get_add_issue_contains_form(self):
        '''
        The add issue view should contain the IssueForm in the page context for get requests.
        '''
        self.client.login(username='TestUser', password='tH1$isA7357')
        response = self.client.get('/issues/add/')
        self.assertIsInstance(response.context['form'], IssueForm)

    def test_post_add_issue_redirects_anonymous(self):
        response = self.client.post('/issues/add/', {'title': 'New Issue', 'content': 'It\'s new!'})
        self.assertRedirects(response, reverse('login') + '?next=/issues/add/')

    def test_post_add_issue_creates_issue(self):
        '''
        Post requests to add issue with valid input should create a new issue, and redirect
        to that issue's page.
        '''
        self.client.login(username='TestUser', password='tH1$isA7357')
        response = self.client.post('/issues/add/', {'title': 'New Issue', 'content': 'It\'s new!'})
        self.assertTrue(Issue.objects.get(title='New Issue'))
        self.assertRedirects(response, Issue.objects.get(title='New Issue').get_absolute_url())

# EDIT ISSUE TESTS #

    def test_get_edit_issue(self):
        '''
        The add issue view should return 403 for anyone who isn't the author or an admin, and
        render the edit_issue.html template for authorised users.
        '''
        response = self.client.get('/issues/1/edit/')
        self.assertEqual(response.status_code, 403)

        self.client.login(username='OtherUser', password='tH1$isA7357')
        response = self.client.get('/issues/1/edit/')
        self.assertEqual(response.status_code, 403)
        self.client.logout()

        self.client.login(username='AdminUser', password='tH1$isA7357')
        response = self.client.get('/issues/1/edit/')
        self.assertEqual(response.status_code, 200)
        self.client.logout()

        self.client.login(username='TestUser', password='tH1$isA7357')
        response = self.client.get('/issues/1/edit/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_issue.html')

    def test_get_edit_issue_contains_form(self):
        '''
        The edit issue view should contain the IssueForm in the page context for get requests.
        '''
        self.client.login(username='TestUser', password='tH1$isA7357')
        response = self.client.get('/issues/1/edit/')
        self.assertIsInstance(response.context['form'], IssueForm)

    def test_post_edit_issue_redirects_anonymous(self):
        '''
        Post requests for unauthorised users should return 403.
        '''
        response = self.client.post('/issues/1/edit/', {'title': 'Updated Issue', 'content': 'It\'s updated!'})
        self.assertEqual(response.status_code, 403)

        self.client.login(username='OtherUser', password='tH1$isA7357')
        response = self.client.post('/issues/1/edit/', {'title': 'Updated Issue', 'content': 'It\'s updated!'})
        self.assertEqual(response.status_code, 403)

    def test_post_edit_issue_updates_issue(self):
        '''
        Post requests to edit issue with valid input should update the issue, set it's edited time to now,
        and redirect to that issue's page.
        '''
        self.client.login(username='TestUser', password='tH1$isA7357')
        response = self.client.post('/issues/1/edit/', {'title': 'Updated Issue', 'content': 'It\'s updated!'})
        self.assertEqual(Issue.objects.get(pk=1).title, 'Updated Issue')
        self.assertEqual(Issue.objects.get(pk=1).content, 'It\'s updated!')
        self.assertTrue(Issue.objects.get(pk=1).edited)
        self.assertRedirects(response, Issue.objects.get(pk=1).get_absolute_url())

# SET ISSUE STATUS TESTS #

    def test_post_set_issue_status(self):
        '''
        Only users with permissions can set issue status, everyone else returns 403 forbidden.
        Authorised users are redirected to the issue.
        '''
        response = self.client.post('/issues/1/approved/')
        self.assertEqual(response.status_code, 403)
        self.client.logout()

        self.client.login(username='OtherUser', password='tH1$isA7357')
        response = self.client.post('/issues/1/approved/')
        self.assertEqual(response.status_code, 403)
        self.client.logout()

        self.client.login(username='TestUser', password='tH1$isA7357')
        response = self.client.post('/issues/1/approved/')
        self.assertEqual(response.status_code, 403)
        self.client.logout()

        self.client.login(username='AdminUser', password='tH1$isA7357')
        response = self.client.post('/issues/1/approved/')
        self.assertRedirects(response, Issue.objects.get(pk=1).get_absolute_url())

    def test_set_issue_updates_issue(self):
        '''
        The set status routes set the issue to the corresponding status.
        '''
        self.client.login(username='AdminUser', password='tH1$isA7357')
        self.client.post('/issues/1/approved/')
        self.assertEqual(Issue.objects.get(pk=1).status, 'approved')

        self.client.post('/issues/2/doing/')
        self.assertEqual(Issue.objects.get(pk=2).status, 'doing')

        self.client.post('/issues/3/done/')
        self.assertEqual(Issue.objects.get(pk=3).status, 'done')

# VOTE FOR ISSUE TESTS #

    def test_post_vote_for_issue(self):
        '''
        The vote route should return 403 for anonymous users, and redirect to the
        issue for everyone else.
        '''
        response = self.client.post('/issues/1/vote/')
        self.assertEqual(response.status_code, 403)
        self.client.logout()

        self.client.login(username='TestUser', password='tH1$isA7357')
        response = self.client.post('/issues/1/vote/')
        self.assertRedirects(response, Issue.objects.get(pk=1).get_absolute_url())

    def test_vote_for_issue_increases_no_votes(self):
        '''
        Voting for an issue should increase it's vote count.
        '''
        initial_votes = Issue.objects.get(pk=2).no_votes
        self.client.login(username='TestUser', password='tH1$isA7357')
        self.client.post('/issues/2/vote/')
        self.assertGreater(Issue.objects.get(pk=2).no_votes, initial_votes)

    def test_users_can_only_vote_once(self):
        '''
        Users can only vote for an issue once, voting again returns a 403 forbidden
        and does not increase the count.
        '''
        self.client.login(username='TestUser', password='tH1$isA7357')
        self.client.post('/issues/3/vote/')
        initial_votes = Issue.objects.get(pk=3).no_votes

        response = self.client.post('/issues/3/vote/')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(initial_votes, Issue.objects.get(pk=3).no_votes)
