from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib import auth
from django.shortcuts import get_object_or_404


class RegistrationViewsTestCase(TestCase):
    '''
    Class to test additional and extended registration views.
    '''

    @classmethod
    def setUpTestData(cls):
        test_user = User.objects.create_user(username='TestUser', email='test@test.com',
                                             password='tH1$isA7357')
        test_user.save()

    def setUp(self):
        self.client.logout()

    def test_login_only_accessible_to_anonymous_users(self):
        '''
        Only anonymous users should have access to the login page,
        authenticated users should recieve a 403 Forbidden error.
        '''
        response = self.client.get('/account/login/')
        self.assertEqual(response.status_code, 200)

        self.client.login(username='TestUser', password='tH1$isA7357')

        response = self.client.get('/account/login/')
        self.assertEqual(response.status_code, 403)

        response = self.client.post('/account/login/', {'username': 'TestUser',
                                                        'password': 'tH1$isA7357'})
        self.assertEqual(response.status_code, 403)

    def test_get_sign_up_page(self):
        '''
        The sign up page should return 200, and use the sign_up.html template.
        '''
        response = self.client.get('/account/sign-up/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/sign_up.html')

    def test_sign_up_only_accessible_to_anonymous_users(self):
        '''
        Only anonymous users should have access to the sign up page,
        authenticated users should recieve a 403 Forbidden error.
        '''
        response = self.client.get('/account/sign-up/')
        self.assertEqual(response.status_code, 200)

        self.client.login(username='TestUser', password='tH1$isA7357')

        response = self.client.get('/account/sign-up/')
        self.assertEqual(response.status_code, 403)

        response = self.client.post('/account/sign-up/', {'username': 'LoggedInUser',
                                                          'email': 'loggedin@test.com',
                                                          'password1': 'tH1$isA7357',
                                                          'password2': 'tH1$isA7357'})
        self.assertEqual(response.status_code, 403)

    def test_post_sign_up_page_creates_user(self):
        '''
        The sign up page should create a new user when given valid data.
        '''
        self.client.post('/account/sign-up/', {'username': 'NewUser',
                                               'email': 'newuser@test.com',
                                               'password1': 'tH1$isA7357',
                                               'password2': 'tH1$isA7357'})

        new_user = get_object_or_404(User, username='NewUser')
        self.assertEqual(new_user.username, 'NewUser')

    def test_post_sign_up_page_logs_user_in_and_redirects_on_success(self):
        '''
        The sign up page should log the new user in and redirect them to the home page.
        '''
        response = self.client.post('/account/sign-up/',
                                    {'username': 'SuccessfulUser', 'email': 'successfuluser@test.com',
                                     'password1': 'tH1$isA7357', 'password2': 'tH1$isA7357'},
                                    follow=True)

        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)
        self.assertIn(('/', 302), response.redirect_chain)

    def test_post_sign_up_page_returns_sign_up_page_on_failure(self):
        '''
        The sign up page should return the user to the sign up page if they fail to create a new user.
        '''
        response = self.client.post('/account/sign-up/',
                                    {'username': 'FailedUser', 'email': 'faileduser@test.com',
                                     'password1': 'tH1$isA7357', 'password2': 'noMatch'},)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/sign_up.html')
