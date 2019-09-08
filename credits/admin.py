from django.contrib import admin
from credits.models import Wallet, Credit, Debit

# Register your models here.


class DebitAdmin(admin.TabularInline):
    model = Debit


class CreditAdmin(admin.TabularInline):
    model = Credit


class WalletAdmin(admin.ModelAdmin):
    model = Wallet
    inlines = (DebitAdmin, CreditAdmin)


admin.site.register(Wallet, WalletAdmin)
