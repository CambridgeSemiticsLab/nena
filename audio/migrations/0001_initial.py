# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dialects', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Audio',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=255, blank=True)),
                ('dialect', models.ForeignKey(to='dialects.Dialect', on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='Recording',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data', models.FileField(upload_to=b'media/')),
                ('audio', models.ForeignKey(to='audio.Audio', on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='Transcript',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language', models.CharField(max_length=50)),
                ('transcript', models.TextField(max_length=78)),
                ('recording', models.ForeignKey(to='audio.Recording', on_delete=models.CASCADE)),
            ],
        ),
    ]
