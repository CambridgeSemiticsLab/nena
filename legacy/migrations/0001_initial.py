# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-04-12 09:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AudioFiles',
            fields=[
                ('file_id', models.AutoField(primary_key=True, serialize=False)),
                ('transcript', models.TextField(blank=True, null=True)),
                ('translation', models.TextField(blank=True, null=True)),
                ('filename', models.CharField(blank=True, max_length=160, null=True)),
                ('filesize', models.CharField(blank=True, max_length=50, null=True)),
                ('filetype', models.CharField(blank=True, max_length=50, null=True)),
                ('audio_url', models.CharField(blank=True, max_length=255, null=True)),
                ('audio_link', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'db_table': 'audio_files',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='AudioMaterial',
            fields=[
                ('audio_id', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=160)),
                ('description', models.TextField(blank=True, null=True)),
                ('image_id', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'audio_material',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Dialectmaps',
            fields=[
                ('map_id', models.AutoField(primary_key=True, serialize=False)),
                ('map_title', models.CharField(max_length=80)),
                ('map_notes', models.CharField(blank=True, max_length=255, null=True)),
                ('map_author', models.CharField(blank=True, max_length=80, null=True)),
                ('map_savedate', models.DateField()),
                ('map_strdata', models.TextField()),
                ('map_postdata', models.TextField()),
            ],
            options={
                'db_table': 'dialectmaps',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Dialects',
            fields=[
                ('dialect_id', models.AutoField(primary_key=True, serialize=False)),
                ('dialect', models.CharField(max_length=80)),
                ('community', models.CharField(blank=True, max_length=80, null=True)),
                ('country', models.CharField(blank=True, max_length=160, null=True)),
                ('location', models.CharField(blank=True, max_length=160, null=True)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
                ('source', models.TextField(blank=True, null=True)),
                ('information', models.TextField(blank=True, null=True)),
                ('general_remarks', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'dialect',
                'verbose_name_plural': 'dialects',
                'db_table': 'dialects',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='ExtAudioMaterial',
            fields=[
                ('ext_audio_id', models.AutoField(primary_key=True, serialize=False)),
                ('link_url', models.CharField(max_length=255)),
                ('link_text', models.CharField(max_length=255)),
                ('link_description', models.TextField()),
            ],
            options={
                'db_table': 'ext_audio_material',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='GrammarFeatureEntries',
            fields=[
                ('entry_id', models.AutoField(primary_key=True, serialize=False)),
                ('entry', models.CharField(max_length=160)),
                ('comment', models.TextField(blank=True, null=True)),
                ('frequency', models.CharField(max_length=30)),
            ],
            options={
                'verbose_name': 'grammar feature entry',
                'verbose_name_plural': 'grammar feature entries',
                'db_table': 'grammar_feature_entries',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='GrammarFeatureExamples',
            fields=[
                ('example_id', models.AutoField(primary_key=True, serialize=False)),
                ('example', models.CharField(max_length=160)),
            ],
            options={
                'verbose_name': 'grammar feature example',
                'verbose_name_plural': 'grammar feature examples',
                'db_table': 'grammar_feature_examples',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='GrammarFeatures',
            fields=[
                ('feature_id', models.AutoField(primary_key=True, serialize=False)),
                ('introduction', models.TextField(blank=True, null=True)),
                ('comment', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'grammar feature',
                'verbose_name_plural': 'grammar features',
                'db_table': 'grammar_features',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Headers',
            fields=[
                ('header_id', models.AutoField(primary_key=True, serialize=False)),
                ('header_level', models.IntegerField()),
                ('header', models.CharField(max_length=255)),
                ('seq_no', models.IntegerField()),
                ('level0_seq', models.IntegerField()),
                ('level1_seq', models.IntegerField()),
                ('level2_seq', models.IntegerField()),
                ('level3_seq', models.IntegerField()),
                ('level4_seq', models.IntegerField()),
                ('level5_seq', models.IntegerField()),
                ('group_header', models.IntegerField()),
                ('end_paragraph', models.IntegerField()),
            ],
            options={
                'verbose_name': 'header',
                'verbose_name_plural': 'headers',
                'db_table': 'headers',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Images',
            fields=[
                ('image_id', models.AutoField(primary_key=True, serialize=False)),
                ('image', models.CharField(max_length=255)),
                ('type', models.CharField(max_length=255)),
                ('caption', models.CharField(max_length=255)),
                ('tags', models.CharField(blank=True, max_length=255, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('source', models.CharField(blank=True, max_length=255, null=True)),
                ('date_created', models.DateField(blank=True, null=True)),
                ('location', models.CharField(blank=True, max_length=255, null=True)),
                ('date_added', models.DateField()),
            ],
            options={
                'db_table': 'images',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Images2',
            fields=[
                ('image_id', models.AutoField(primary_key=True, serialize=False)),
                ('image', models.CharField(max_length=255)),
                ('image_small', models.CharField(max_length=255)),
                ('description', models.CharField(max_length=255)),
                ('source', models.CharField(max_length=255)),
                ('date_created', models.DateField()),
            ],
            options={
                'db_table': 'images2',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Imagestest',
            fields=[
                ('image_id', models.AutoField(primary_key=True, serialize=False)),
                ('image', models.CharField(max_length=255)),
                ('type', models.CharField(max_length=255)),
                ('caption', models.CharField(max_length=255)),
                ('notes', models.TextField(blank=True, null=True)),
                ('source', models.CharField(blank=True, max_length=255, null=True)),
                ('date_created', models.DateField(blank=True, null=True)),
                ('location', models.CharField(blank=True, max_length=255, null=True)),
                ('date_added', models.DateField()),
            ],
            options={
                'db_table': 'imagestest',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Introduction',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=100)),
                ('introdata', models.TextField()),
                ('photo', models.CharField(blank=True, max_length=100, null=True)),
                ('caption', models.CharField(blank=True, max_length=100, null=True)),
                ('publishdate', models.DateField()),
            ],
            options={
                'db_table': 'introduction',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='News',
            fields=[
                ('news_id', models.AutoField(primary_key=True, serialize=False)),
                ('news_type', models.CharField(max_length=80)),
                ('title', models.CharField(max_length=80)),
                ('short_description', models.CharField(max_length=255)),
                ('news', models.TextField(blank=True, null=True)),
                ('link', models.CharField(blank=True, max_length=255, null=True)),
                ('publish_date', models.DateField()),
                ('expiry_date', models.DateField()),
            ],
            options={
                'db_table': 'news',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Researchteam',
            fields=[
                ('rtid', models.AutoField(primary_key=True, serialize=False)),
                ('listposition', models.IntegerField()),
                ('rtname', models.CharField(max_length=50)),
                ('rttype', models.CharField(max_length=50)),
                ('rtposition', models.CharField(blank=True, max_length=100, null=True)),
                ('rtaddress', models.CharField(blank=True, max_length=100, null=True)),
                ('rtemail', models.CharField(blank=True, max_length=25, null=True)),
                ('rtphone', models.CharField(blank=True, max_length=25, null=True)),
                ('rtphoto', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'db_table': 'researchteam',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Sitehelp',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=100)),
                ('shdata', models.TextField()),
                ('photo', models.CharField(blank=True, max_length=100, null=True)),
                ('caption', models.CharField(blank=True, max_length=100, null=True)),
                ('publishdate', models.DateField()),
            ],
            options={
                'db_table': 'sitehelp',
                'managed': False,
            },
        ),
    ]
