from django.test import TestCase
from django.contrib.auth.models import User
from credits.models import Wallet, Credit, Debit
from django.utils import timezone
from datetime import timedelta


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


class CreditTestCase(TestCase):
    '''
    Class to test Credit model.
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

    def test_credit_str_returns_amount_credited_to_user_at_time(self):
        '''
        A credit's str function should return x Credits to User @ time.
        '''
        transaction = Credit.objects.create(wallet=self.test_user.wallet, amount=6)
        transaction.save()

        self.assertRegex(str(transaction), '^6 Credits to TestUser @ [0-9]{2}/[0-9]{2}/[0-9]{2} [0-9]{2}:[0-9]{2}$')

    def test_credit_not_refundable_if_already_refunded(self):
        '''
        A shouldn't be refundable if it has already bene refunded.
        '''
        transaction = Credit.objects.create(wallet=self.test_user.wallet, amount=3, stripe_transaction_id='ch_1FbZgDBuihlwtaswn9FPjLHN')
        transaction.refunded = True
        transaction.save()
        self.test_user.wallet.balance = 10
        self.test_user.wallet.save()

        self.assertFalse(transaction.can_refund)

    def test_credit_not_refundable_if_insuficient_credits(self):
        '''
        Credits should not be refundable if the user's wallet doesn't have enough credits.
        '''
        transaction = Credit.objects.create(wallet=self.test_user.wallet, amount=5, stripe_transaction_id='ch_1FbZgDBuihlwtaswn9FPjLHN')
        transaction.save()
        self.test_user.wallet.balance = 0
        self.test_user.wallet.save()

        self.assertFalse(transaction.can_refund)

    def test_credit_not_refundable_after_90_days(self):
        '''
        Credits should not be refundable after 90 days.
        '''
        transaction = Credit.objects.create(wallet=self.test_user.wallet, amount=10, stripe_transaction_id='ch_1FbZgDBuihlwtaswn9FPjLHN')
        transaction.created = timezone.now() - timedelta(days=91)
        transaction.save()
        self.test_user.wallet.balance = 20
        self.test_user.wallet.save()

        self.assertFalse(transaction.can_refund)

    def test_credit_non_refundable_without_associated_transaction_id(self):
        '''
        Credits should not be refundable without a stripe id.
        '''
        transaction = Credit.objects.create(wallet=self.test_user.wallet, amount=15)
        transaction.save()
        self.test_user.wallet.balance = 20
        self.test_user.wallet.save()

        self.assertFalse(transaction.can_refund)

    def test_credit_can_be_refunded(self):
        '''
        Otherwise a credit can be refunded if within 90 days, the user has the credits available, and there is a valid transaction id.
        '''
        transaction = Credit.objects.create(wallet=self.test_user.wallet, amount=11, stripe_transaction_id='ch_1FbZgDBuihlwtaswn9FPjLHN')
        transaction.save()
        self.test_user.wallet.balance = 20
        self.test_user.wallet.save()

        self.assertTrue(transaction.can_refund)
