# Generated by Django 2.1.7 on 2019-05-10 14:12
from django.db import migrations

from ftfy import fix_text

from dialects.models import DialectFeatureEntry

cleaners = (
    ('\<sup\>\+\<\/sup\>', lambda entry: entry.lower().replace('<sup>+</sup>', '⁺')),
    ('\<sup\>y\<\/sup\>', lambda entry: entry.lower().replace('<sup>y</sup>', 'ʸ')),
    ('\<span class=aramaic\>', lambda entry: entry.lower().replace('<span class=aramaic>', '')),
    ('\<\/span\>', lambda entry: entry.lower().replace('</span>', '')),
    ('\<span\>', lambda entry: entry.lower().replace('<span>', '')),
)

def forwards(apps, schema_editor):
    for regex, cleaning_function in cleaners:
        dfes = DialectFeatureEntry.objects.filter(entry__iregex=regex)
        print('\nLooking for '+regex)
        for dfe in dfes[0:50000]:
            print(dfe)
            print('  was: ' + dfe.entry[0:100])
            dfe.entry = cleaning_function(dfe.entry)
            print('  now: ' + dfe.entry[0:100])
            dfe.save()

def backwards(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('dialects', '0011_auto_20190312_0713'),
    ]

    operations = [
       migrations.RunPython(forwards, backwards),
    ]