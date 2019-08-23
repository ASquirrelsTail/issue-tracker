from django.test import TestCase
from django.contrib.auth.models import User
from account.forms import UserSignUpForm


class UserSignUpFormTestCase(TestCase):
    '''
    Class to test user sign up form.
    '''

    def test_requires_email(self):
        '''
        The email field is required, and submitted forms should only be valid if it is completed
        '''
        form = UserSignUpForm({'username': 'test', 'password1': 'tH1$isA7357', 'password2': 'tH1$isA7357'})
        self.assertFalse(form.is_valid())
        form = UserSignUpForm({'username': 'test', 'email': 'test@test.com',
                               'password1': 'tH1$isA7357', 'password2': 'tH1$isA7357'})
        self.assertTrue(form.is_valid())

    def test_email_must_be_unique(self):
        '''
        The email cannot already have a user assoctaed with it.
        '''
        test_user = User.objects.create_user(username='ExistingUser', email='test@test.com',
                                             password='tH1$isA7357')
        test_user.save()

        form = UserSignUpForm({'username': 'test', 'email': 'test@test.com',
                               'password1': 'tH1$isA7357', 'password2': 'tH1$isA7357'})
        self.assertFalse(form.is_valid())
