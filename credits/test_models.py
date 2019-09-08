from django.test import TestCase
from django.contrib.auth.models import User
from credits.models import Wallet


class WalletModelTestCase(TestCase):
    '''
    Class to test the wallet model.
    '''

    @classmethod
    def setUpTestData(cls):
        cls.test_user = User.objects.create_user(username='TestUser', email='test@test.com',
                                                 password='tH1$isA7357')

        Wallet.objects.create(user=cls.test_user)

    def setUp(self):
        wallet = Wallet.objects.get(user=self.test_user)
        wallet.amount = 0
        wallet.save()

    def test_wallet_str_returns_users_wallet(self):
        '''
        A Wallet's str function should return {user}'s wallet
        '''
        wallet = Wallet.objects.get(user=self.test_user)

        self.assertEqual(str(wallet), 'TestUser\'s wallet')

    def test_credit_increases_wallet_amount(self):
        '''
        Crediting a users wallet increases the amount in it.
        '''
        wallet = Wallet.objects.get(user=self.test_user)

        wallet.credit(10)
        self.assertEqual(wallet.amount, 10)

    def test_debit_decreases_wallet_amount(self):
        '''
        Debiting a users wallet decreases the amount in it.
        '''
        wallet = Wallet.objects.get(user=self.test_user)

        wallet.credit(10)
        wallet.debit(5)
        self.assertEqual(wallet.amount, 5)

    def test_debit_fails_if_wallet_amount_insufficient(self):
        wallet = Wallet.objects.get(user=self.test_user)
        self.assertFalse(wallet.debit(5))
        wallet = Wallet.objects.get(user=self.test_user)
        self.assertEqual(0, wallet.amount)
