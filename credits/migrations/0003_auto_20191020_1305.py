# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2019-10-20 13:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('credits', '0002_credit_refunded'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='wallet',
            options={'permissions': (('cant_have_wallet', "User can't have a wallet."), ('can_view_transactions_stats', 'User can view all transaction stats'))},
        ),
        migrations.AddField(
            model_name='debit',
            name='real_value',
            field=models.IntegerField(default=0),
        ),
    ]