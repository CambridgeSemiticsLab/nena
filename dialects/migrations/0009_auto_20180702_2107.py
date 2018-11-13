# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-07-02 21:07
from __future__ import unicode_literals

import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dialects', '0008_auto_20180702_2003'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dialect',
            name='information',
            field=ckeditor.fields.RichTextField(blank=True),
        ),
        migrations.AlterField(
            model_name='dialect',
            name='remarks',
            field=ckeditor.fields.RichTextField(blank=True),
        ),
        migrations.AlterField(
            model_name='dialect',
            name='source',
            field=ckeditor.fields.RichTextField(blank=True),
        ),
        migrations.AlterField(
            model_name='dialectfeature',
            name='comment',
            field=ckeditor.fields.RichTextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='dialectfeature',
            name='introduction',
            field=ckeditor.fields.RichTextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='dialectfeatureentry',
            name='comment',
            field=ckeditor.fields.RichTextField(blank=True, null=True),
        ),
    ]
