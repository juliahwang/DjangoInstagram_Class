# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-27 03:28
from __future__ import unicode_literals

from django.db import migrations
import utils.fields.custom_imagefield


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0010_post_video'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='photo',
            field=utils.fields.custom_imagefield.CustomImageField(blank=True, upload_to='post'),
        ),
    ]
