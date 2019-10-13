from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm


class LoginModalContextTestCase(TestCase):
    '''
    Class to test the modal login form context.
    '''

    @classmethod
    def setUpTestData(cls):
        test_user = User.objects.create_user(username='TestContextUser', email='testcontext@test.com',
                                             password='tH1$isA7357')
        test_user.save()

    def setUp(self):
        self.client.logout()

    def test_login_form_provided_to_context(self):
        '''
        The login form should be provided to template contexts for use in the login modal.
        '''
        response = self.client.get('/tickets/')
        self.assertIsInstance(response.context['login_form'], AuthenticationForm)

    def test_login_modal_form_not_provided_for_authenticated_user(self):
        '''
        The login modal form shouldn't be added to the context where a user is already logged in.
        '''
        self.client.login(username='TestContextUser', password='tH1$isA7357')

        response = self.client.get('/tickets/')
        self.assertFalse(response.context['login_form'])

    def test_login_modal_form_not_provided_on_login_page(self):
        '''
        The login modal form shouldn't be added to the context on the login page.
        '''
        response = self.client.get('/account/login/')
        self.assertFalse(response.context.get('login_form'))

    def test_login_modal_next_preserves_path(self):
        '''
        The login modal next value should pass the current path.
        '''
        response = self.client.get('/tickets/')
        self.assertEqual(response.context['login_next'], '/tickets/')

    def test_login_modal_next_ignors_account_paths(self):
        '''
        The login modal shouldn't pass account paths to the next field in the login form.
        '''
        response = self.client.get('/account/sign-up/')
        self.assertFalse(response.context.get('login_next'))
