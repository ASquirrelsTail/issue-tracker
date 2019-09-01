from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Wallet(models.Model):
    user = models.OneToOneField(User)
    ammount = models.IntegerField(default=0)

    def __str__(self):
        return '{}\'s wallet'.format(self.user.username)

    def credit(self, value=0, real_value=0):
        '''
        Credits the user an ammount.
        '''
        self.ammount += value
        Credit.objects.create(wallet=self, ammount=value)
        self.save()

    def debit(self, value=0):
        '''
        Debits an ammount from the users wallet.
        '''
        self.ammount -= value
        Debit.objects.create(wallet=self, ammount=value)
        self.save()


class Transaction(models.Model):
    wallet = models.ForeignKey(Wallet)
    created = models.DateTimeField(auto_now_add=True)
    ammount = models.IntegerField(default=0)

    class Meta:
        abstract = True


class Credit(Transaction):
    real_value = models.IntegerField(default=0)
    stripe_transaction_id = models.CharField(max_length=50, null=True, default=None)


class Debit(Transaction):
    pass
