# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-26 15:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0006_comment_html_content'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='content',
            field=models.TextField(blank=True),
        ),
    ]
