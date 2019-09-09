from django.contrib import admin
from credits.models import Wallet, Credit, Debit

# Register your models here.


class DebitAdmin(admin.TabularInline):
    model = Debit
    readonly_fields = ('wallet', 'created', 'amount',)


class CreditAdmin(admin.TabularInline):
    model = Credit
    readonly_fields = ('wallet', 'created', 'amount', 'real_value', 'stripe_transaction_id',)


class WalletAdmin(admin.ModelAdmin):
    model = Wallet
    readonly_fields = ('user', 'balance',)
    inlines = (DebitAdmin, CreditAdmin)


admin.site.register(Wallet, WalletAdmin)
