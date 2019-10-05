# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2019-10-05 18:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0006_auto_20190928_1540'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='label',
            options={'permissions': (('can_create_edit_delete_labels', 'Create, edit and delete labels.'),)},
        ),
        migrations.AddField(
            model_name='ticket',
            name='labels',
            field=models.ManyToManyField(to='tickets.Label'),
        ),
        migrations.AlterField(
            model_name='label',
            name='name',
            field=models.CharField(max_length=30, unique=True),
        ),
    ]
