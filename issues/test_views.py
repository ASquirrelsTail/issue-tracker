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

# ISSUE DETAIL VIEW TESTS #

    def test_get_issue_detail(self):
        '''
        The issue detail view should return 200, and use the issue_detail.html yemplate
        '''
        response = self.client.get('/issues/1/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'issue_detail.html')

    def test_issue_detail_contains_issue(self):
        '''
        The issue detail view should pass the issue to the page context
        '''
        response = self.client.get('/issues/1/')
        self.assertEqual(response.context['object'], Issue.objects.get(pk=1))

    def test_issue_detail_has_comment_form_if_logged_in(self):
        '''
        The issue detail view should pass the comment form to the page context only if the
        user is logged in.
        '''
        response = self.client.get('/issues/1/')
        self.assertIsNone(response.context.get('comment_form'))

        self.client.login(username='TestUser', password='tH1$isA7357')
        response = self.client.get('/issues/1/')
        self.assertIsInstance(response.context['comment_form'], CommentForm)

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

    def test_post_edit_issue_anonymous_forbidden(self):
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

        cls.test_issue1 = Issue(user=cls.test_user, title='Test title 1', content='Test content 1')
        cls.test_issue1.save()

        cls.test_issue2 = Issue(user=cls.test_user, title='Test title 2', content='Test content 2')
        cls.test_issue2.save()

    def setUp(self):
        self.client.logout()

    def test_get_add_comment(self):
        '''
        The add comment route should return 403 for anonymous users, and render the
        add_comment.html template for everyone else.
        '''
        response = self.client.get('/issues/1/comments/add/')
        self.assertEqual(response.status_code, 403)

        self.client.login(username='TestUser', password='tH1$isA7357')
        response = self.client.get('/issues/1/comments/add/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'add_comment.html')
        self.assertIsInstance(response.context['form'], CommentForm)

    def test_add_comment_non_existent_issue_not_found(self):
        '''
        The add comment route should return 404 if the issue doesn't exist.
        '''
        self.client.login(username='TestUser', password='tH1$isA7357')
        response = self.client.get('/issues/999/comments/add/')
        self.assertEqual(response.status_code, 404)

    def test_post_add_comment(self):
        '''
        Post requests for add comment should create that comment and redirect to the issue.
        '''
        self.client.login(username='TestUser', password='tH1$isA7357')
        response = self.client.post('/issues/1/comments/add/', {'content': 'A test comment.'})
        self.assertTrue(Comment.objects.get(content='A test comment.'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, Comment.objects.get(content='A test comment.').get_absolute_url())

    def test_post_add_comment_to_non_existent_issue_fails(self):
        '''
        Post requests for add comment for non existent issues should fail.
        '''
        self.client.login(username='TestUser', password='tH1$isA7357')
        response = self.client.post('/issues/999/comments/add/', {'content': 'This issue never existed!'})
        self.assertFalse(Comment.objects.filter(content='This issue never existed!'))
        self.assertEqual(response.status_code, 404)

    def test_get_post_add_comment_reply_to_non_existent_comment(self):
        '''
        The reply to comment route should return 404 if the parent comment is not found
        '''
        self.client.login(username='TestUser', password='tH1$isA7357')
        response = self.client.get('/issues/2/comments/999/reply/')
        self.assertEqual(response.status_code, 404)
        response = self.client.post('/issues/2/comments/999/reply/', {'content': 'Nothing to reply to!'})
        self.assertEqual(response.status_code, 404)

    def test_post_reply_add_comment_includes_parent(self):
        '''
        Post requests for add reply to comment should create that reply and redirect to the issue.
        The reply should reference its parent.
        '''
        test_comment = Comment(user=self.other_user, issue=self.test_issue2, content='A test parent comment.')
        test_comment.save()
        test_comment = Comment.objects.get(content='A test parent comment.')

        self.client.login(username='TestUser', password='tH1$isA7357')
        response = self.client.post('/issues/2/comments/{}/reply/'.format(test_comment.id),
                                    {'content': 'A test reply.'})
        self.assertTrue(Comment.objects.get(reply_to=test_comment))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, Comment.objects.get(reply_to=test_comment).get_absolute_url())
        self.assertEqual(Comment.objects.get(reply_to=test_comment).reply_to, test_comment)

    def test_get_post_reply_add_comment_to_mismatched_issue_fails(self):
        '''
        Get and post requests for add reply to comment for non mismatched issues should fail with a 400 bad request.
        '''
        test_comment = Comment(user=self.other_user, issue=self.test_issue2, content='A comment on issue 2.')
        test_comment.save()
        test_comment = Comment.objects.get(content='A comment on issue 2.')

        self.client.login(username='TestUser', password='tH1$isA7357')
        response = self.client.get('/issues/1/comments/{}/reply/'.format(test_comment.id))
        self.assertEqual(response.status_code, 400)
        response = self.client.post('/issues/1/comments/{}/reply/'.format(test_comment.id),
                                    {'content': 'A reply to the comment on issue 2 for issue 1.'})
        self.assertFalse(Comment.objects.filter(content='A reply to the comment on issue 2 for issue 1.'))
        self.assertEqual(response.status_code, 400)

    def test_get_post_reply_add_comment_reply_to_reply_fails(self):
        test_comment = Comment(user=self.other_user, issue=self.test_issue2, content='A primary comment on issue 2.')
        test_comment.save()
        test_comment = Comment.objects.get(content='A primary comment on issue 2.')
        test_reply = Comment(user=self.other_user, issue=self.test_issue2,
                             reply_to=test_comment, content='A reply to comment on issue 2.')
        test_reply.save()
        test_reply = Comment.objects.get(content='A reply to comment on issue 2.')

        self.client.login(username='TestUser', password='tH1$isA7357')
        response = self.client.get('/issues/2/comments/{}/reply/'.format(test_reply.id))
        self.assertEqual(response.status_code, 400)
        response = self.client.post('/issues/2/comments/{}/reply/'.format(test_reply.id),
                                    {'content': 'A reply to a reply.'})
        self.assertFalse(Comment.objects.filter(content='A reply to a reply.'))
        self.assertEqual(response.status_code, 400)

    def test_get_edit_comment(self):
        '''
        The edit comment view should return 403 for anyone who isn't the author or an admin, and
        render the edit_comment.html template for authorised users, and include the comment form.
        '''
        test_comment = Comment(user=self.test_user, issue=self.test_issue2, content='A comment by TestUser.')
        test_comment.save()
        test_comment = Comment.objects.get(content='A comment by TestUser.')

        response = self.client.get('/issues/2/comments/{}/edit/'.format(test_comment.id))
        self.assertEqual(response.status_code, 403)

        self.client.login(username='OtherUser', password='tH1$isA7357')
        response = self.client.get('/issues/2/comments/{}/edit/'.format(test_comment.id))
        self.assertEqual(response.status_code, 403)
        self.client.logout()

        self.client.login(username='AdminUser', password='tH1$isA7357')
        response = self.client.get('/issues/2/comments/{}/edit/'.format(test_comment.id))
        self.assertEqual(response.status_code, 200)
        self.client.logout()

        self.client.login(username='TestUser', password='tH1$isA7357')
        response = self.client.get('/issues/2/comments/{}/edit/'.format(test_comment.id))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_comment.html')
        self.assertIsInstance(response.context['form'], CommentForm)

    def test_post_edit_comment_anonymous_forbidden(self):
        '''
        Post requests for unauthorised users should return 403.
        '''
        test_comment = Comment(user=self.test_user, issue=self.test_issue2, content='Another comment by TestUser.')
        test_comment.save()
        test_comment = Comment.objects.get(content='Another comment by TestUser.')

        response = self.client.post('/issues/2/comments/{}/edit/'.format(test_comment.id), {'content': 'It\'s edited!'})
        self.assertEqual(response.status_code, 403)

        self.client.login(username='OtherUser', password='tH1$isA7357')
        response = self.client.post('/issues/2/comments/{}/edit/'.format(test_comment.id), {'content': 'It\'s edited!'})
        self.assertEqual(response.status_code, 403)

    def test_post_edit_comment_updates_comment(self):
        '''
        Post requests to edit comment with valid input should update the comment, set it's edited time to now,
        and redirect to that comment's page.
        '''
        test_comment = Comment(user=self.test_user, issue=self.test_issue2, content='A final comment by TestUser.')
        test_comment.save()
        test_comment = Comment.objects.get(content='A final comment by TestUser.')

        self.client.login(username='TestUser', password='tH1$isA7357')
        response = self.client.post('/issues/2/comments/{}/edit/'.format(test_comment.id), {'content': 'Successfully edited!'})
        self.assertEqual(Comment.objects.get(pk=test_comment.id).content, 'Successfully edited!')
        self.assertTrue(Comment.objects.get(pk=test_comment.id).edited)
        self.assertRedirects(response, Comment.objects.get(pk=test_comment.id).get_absolute_url())
