# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2019-08-26 17:41
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('issues', '0007_vote'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='reply_to',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='replies', to='issues.Comment'),
        ),
    ]
