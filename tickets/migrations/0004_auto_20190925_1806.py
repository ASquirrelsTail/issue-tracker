# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2019-09-25 18:06
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0003_auto_20190924_0926'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ticket',
            options={'ordering': ['-created'], 'permissions': (('can_update_status', 'Update Ticket status.'), ('can_edit_all_tickets', "Edit any user's ticket"), ('can_view_all_stats', 'View stats for any ticket'))},
        ),
    ]
