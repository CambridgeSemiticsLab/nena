# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-07-18 04:18
from __future__ import unicode_literals

import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('audio', '0003_auto_20180718_0413'),
    ]

    operations = [
        migrations.AlterField(
            model_name='audio',
            name='transcript',
            field=ckeditor.fields.RichTextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='audio',
            name='translation',
            field=ckeditor.fields.RichTextField(blank=True, null=True),
        ),
    ]
