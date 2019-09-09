from django.test import TestCase
from django.contrib.auth.models import User, Permission
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
        Anonymous users have no wallet balance.
        '''
        response = self.client.get('/')
        self.assertIsNone(response.context.get('wallet_balance'))

    def test_authenticated_user_returns_wallet_balance(self):
        '''
        A users wallet balance is added to the context when they are authenticated.
        '''
        self.client.login(username='TestContextUser', password='tH1$isA7357')

        response = self.client.get('/')
        self.assertEqual(response.context.get('wallet_balance'), 0)

        self.test_user.wallet.credit(10)
        response = self.client.get('/')
        self.assertEqual(response.context.get('wallet_balance'), 10)

    def test_admin_user_returns_wallet_balance_none(self):
        '''
        An admin user with can't have wallet permission returns a wallet balance of None.
        '''
        admin_user = User.objects.create_user(username='AdminUser', email='admin@test.com',
                                              password='tH1$isA7357')
        admin_user.save()

        admin_user.user_permissions.set(Permission.objects.all())

        self.client.login(username='admin_user', password='tH1$isA7357')

        response = self.client.get('/')
        self.assertIsNone(response.context.get('wallet_balance'))

    def test_user_has_no_wallet_wallet_balance_is_zero(self):
        '''
        A user without a wallet returns a wallet balance of zero.
        '''
        no_wallet_user = User.objects.create_user(username='NoWalletUser', email='nowallet@test.com',
                                                  password='tH1$isA7357')
        no_wallet_user.save()

        self.client.login(username='NoWalletUser', password='tH1$isA7357')

        response = self.client.get('/')
        self.assertEqual(response.context.get('wallet_balance'), 0)
