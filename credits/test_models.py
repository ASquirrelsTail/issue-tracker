from django.test import TestCase
from django.contrib.auth.models import User
from credits.models import Wallet, Credit, Debit


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
        wallet.balance = 0
        wallet.save()

    def test_wallet_str_returns_users_wallet(self):
        '''
        A Wallet's str function should return {user}'s wallet
        '''
        wallet = Wallet.objects.get(user=self.test_user)

        self.assertEqual(str(wallet), 'TestUser\'s wallet')

    def test_credit_increases_wallet_balance(self):
        '''
        Crediting a users wallet increases its balance.
        '''
        wallet = Wallet.objects.get(user=self.test_user)

        wallet.credit(10)
        self.assertEqual(wallet.balance, 10)

    def test_credit_creates_credit_transaction(self):
        '''
        Crediting a user's wallet creates a credit transaction with
        the details of the transaction.
        '''
        wallet = Wallet.objects.get(user=self.test_user)

        wallet.credit(10, 60, 'ch_1FGssUBuihlwtaswUpgBYH9T')
        self.assertTrue(Credit.objects.get(wallet=wallet, amount=10, stripe_transaction_id='ch_1FGssUBuihlwtaswUpgBYH9T'))

    def test_debit_decreases_wallet_balance(self):
        '''
        Debiting a users wallet decreases its balance.
        '''
        wallet = Wallet.objects.get(user=self.test_user)

        wallet.credit(10)
        wallet.debit(5)
        self.assertEqual(wallet.balance, 5)
        wallet.debit(5)
        self.assertEqual(wallet.balance, 0)

    def test_debit_creates_debit_transaction(self):
        '''
        Debiting a user's wallet creates a debit transaction with
        the details of the transaction.
        '''
        wallet = Wallet.objects.get(user=self.test_user)

        # It's easier to test debit objects using unique ammounts, than finding the transaction basedon its time of creation
        wallet.credit(42)
        wallet.debit(42)
        self.assertTrue(Debit.objects.get(wallet=wallet, amount=42))

    def test_debit_returns_debit_object_on_success(self):
        '''
        A successful debit returns the remaining balance in the wallet.
        '''
        wallet = Wallet.objects.get(user=self.test_user)

        wallet.credit(10)
        self.assertIsInstance(wallet.debit(5), Debit)

    def test_debit_fails_if_wallet_balance_insufficient(self):
        '''
        Debiting a user's wallet with insufficient funds should return false,
        not change the wallet balance, and not create a debit transaction.
        '''
        wallet = Wallet.objects.get(user=self.test_user)
        self.assertFalse(wallet.debit(39))
        wallet = Wallet.objects.get(user=self.test_user)
        self.assertEqual(0, wallet.balance)
        with self.assertRaises(Debit.DoesNotExist):
            Debit.objects.get(wallet=wallet, amount=39)

        wallet.credit(20)
        self.assertFalse(wallet.debit(21))
        wallet = Wallet.objects.get(user=self.test_user)
        self.assertEqual(20, wallet.balance)
