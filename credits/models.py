from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
import stripe

stripe.api_key = settings.STRIPE_SECRET

# Create your models here.


class Wallet(models.Model):
    user = models.OneToOneField(User)
    balance = models.IntegerField(default=0)

    class Meta:
        permissions = (('cant_have_wallet', 'User can\'t have a wallet.'),
                       ('can_view_transactions_stats', 'User can view all transaction stats'))

    def __str__(self):
        return '{}\'s wallet'.format(self.user.username)

    def credit(self, amount=0, real_value=0, transaction_id=None):
        '''
        Credits the user an amount.
        '''
        self.balance += amount
        transaction = Credit.objects.create(wallet=self, amount=amount, real_value=real_value, stripe_transaction_id=transaction_id)
        transaction.save()
        self.save()
        return self.balance

    def debit(self, amount=0, real_value=0):
        '''
        Debits an amount from the users wallet.
        '''
        if self.balance >= amount:
            self.balance -= amount
            transaction = Debit.objects.create(wallet=self, amount=amount, real_value=real_value)
            transaction.save()
            self.save()
            return transaction
        else:
            return False


class Transaction(models.Model):
    wallet = models.ForeignKey(Wallet)
    created = models.DateTimeField(auto_now_add=True)
    amount = models.IntegerField(default=0)
    real_value = models.IntegerField(default=0)

    class Meta:
        abstract = True


class Credit(Transaction):
    refunded = models.BooleanField(default=False)
    stripe_transaction_id = models.CharField(max_length=50, null=True, default=None)

    @property
    def can_refund(self):
        return self.wallet.balance >= self.amount and self.stripe_transaction_id is not None

    def refund(self):
        if self.can_refund:
            try:
                refund = stripe.Refund.create(charge=self.stripe_transaction_id)
                self.wallet.debit(self.amount, refund['amount'])
                self.refunded = True
                self.save()
                return (refund['status'], refund['amount'])
            except stripe.error.StripeError:
                return (False, 0)
        else:
            return (False, 0)


class Debit(Transaction):
    pass


class PaymentIntentManager(models.Manager):
    def create_payment_intent(self, user, credits, amount):
        '''
        Reuses or creates a payment intent for a new transaction.
        '''
        try:
            payment_intent = self.get(user=user, complete=False)
            payment_intent.update(credits, amount)
        except PaymentIntent.DoesNotExist:
            stripe_payment_intent = stripe.PaymentIntent.create(amount=amount, currency=settings.STRIPE_CURRENCY)
            intent_id = stripe_payment_intent.id
            payment_intent = self.create(user=user, intent_id=intent_id, credits=credits, amount=amount)

        payment_intent.save()
        return payment_intent


class PaymentIntent(models.Model):
    '''
    Model to associate a Stripe payment intent with a prospective transaction.
    '''
    user = models.ForeignKey(User)
    intent_id = models.CharField(max_length=100)
    credits = models.IntegerField(default=0)
    amount = models.IntegerField(default=0)
    complete = models.BooleanField(default=False)

    objects = PaymentIntentManager()

    def retrieve_intent(self):
        '''
        Retrives the actual payment intent from Stripe
        '''
        return stripe.PaymentIntent.retrieve(self.intent_id)

    @property
    def client_secret(self):
        '''
        Returns the client secret from for the payment intent to be used by the stripe.js api to take payment.
        '''
        intent = self.retrieve_intent()
        return intent.client_secret

    def update(self, credits=0, amount=0):
        '''
        Updates the payment intent, both in the DB and in Stripe.
        '''
        stripe.PaymentIntent.modify(self.intent_id, amount=amount)
        self.credits = credits
        self.amount = amount
        self.save()

    def fulfill(self):
        '''
        Completes the payment, checks the correct amount has been recieved, and
        credits the users wallet the correct number of credits.
        '''
        intent = self.retrieve_intent()
        if intent.amount_received == self.amount == intent.charges.data[0].amount:
            wallet = Wallet.objects.get_or_create(user=self.user)[0]
            wallet.credit(self.credits, self.amount, intent.charges.data[0].id)
            self.complete = True
            self.save()
        return self.complete
