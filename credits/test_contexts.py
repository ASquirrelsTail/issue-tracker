from django.test import TestCase
from django.contrib.auth.models import User
from credits.models import Wallet


class WalletContextTestCase(TestCase):
    '''
    Class to test the wallet context.
    '''

    @classmethod
    def setUpTestData(cls):
        cls.test_user = User.objects.create_user(username='TestContextUser', email='testcontext@test.com',
                                                 password='tH1$isA7357')
        cls.test_user.save()

        Wallet.objects.create(user=cls.test_user)

    def setUp(self):
        self.client.logout()

    def test_anonymous_user_no_wallet(self):
        '''
        Anonymous users have no wallet ammount.
        '''
        response = self.client.get('/')
        self.assertIsNone(response.context.get('wallet_ammount'))

    def test_authenticated_user_returns_wallet_ammount(self):
        '''
        A users wallet ammount is added to the context when they are authenticated.
        '''
        self.client.login(username='TestContextUser', password='tH1$isA7357')

        response = self.client.get('/')
        self.assertEqual(response.context.get('wallet_ammount'), 0)

        self.test_user.wallet.credit(10)
        response = self.client.get('/')
        self.assertEqual(response.context.get('wallet_ammount'), 10)
