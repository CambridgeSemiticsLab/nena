# Generated by Django 3.0.5 on 2020-11-11 11:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dialects', '0014_clean_dialectfeatureexamples'),
    ]

    operations = [
        migrations.AddField(
            model_name='dialect',
            name='code',
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
    ]
