# Generated by Django 2.1.7 on 2019-03-12 07:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grammar', '0003_import_headers'),
    ]

    operations = [
        migrations.AddField(
            model_name='feature',
            name='category_list',
            field=models.TextField(blank=True, null=True),
        ),
    ]
