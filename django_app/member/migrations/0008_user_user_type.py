# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-26 05:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('member', '0007_auto_20170623_0522'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='user_type',
            field=models.CharField(choices=[('d', 'Django'), ('f', 'Facebook')], default='d', max_length=1),
        ),
    ]
