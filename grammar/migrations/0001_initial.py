# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-04-14 09:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Feature',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('path', models.CharField(max_length=255, unique=True)),
                ('depth', models.PositiveIntegerField()),
                ('numchild', models.PositiveIntegerField(default=0)),
                ('name', models.CharField(max_length=250)),
                ('heading', models.IntegerField(blank=True, null=True)),
                ('group', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
