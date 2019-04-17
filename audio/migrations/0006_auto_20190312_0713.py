# Generated by Django 2.1.7 on 2019-03-12 07:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('audio', '0005_audio_annotations'),
    ]

    operations = [
        migrations.AlterField(
            model_name='audio',
            name='annotations',
            field=models.FileField(blank=True, null=True, upload_to='annotations/'),
        ),
        migrations.AlterField(
            model_name='audio',
            name='data',
            field=models.FileField(upload_to='audio/'),
        ),
    ]