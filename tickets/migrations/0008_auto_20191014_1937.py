# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2019-10-14 19:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0007_auto_20191005_1831'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='labels',
            field=models.ManyToManyField(blank=True, to='tickets.Label'),
        ),
    ]
