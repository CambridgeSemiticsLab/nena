# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-10-10 13:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('audio', '0004_auto_20180718_0418'),
    ]

    operations = [
        migrations.AddField(
            model_name='audio',
            name='annotations',
            field=models.FileField(blank=True, null=True, upload_to='media/annotations/'),
        ),
    ]
