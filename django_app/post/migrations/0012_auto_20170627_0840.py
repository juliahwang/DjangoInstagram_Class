# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-27 08:40
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0011_auto_20170627_0328'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='post.Post'),
        ),
    ]