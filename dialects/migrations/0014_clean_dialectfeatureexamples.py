from django.db import migrations

from dialects.models import DialectFeatureExample

cleaners = (
    ('\<sup\>\+\<\/sup\>', lambda entry: entry.lower().replace('<sup>+</sup>', '⁺')),
    ('\<sup\>y\<\/sup\>', lambda entry: entry.lower().replace('<sup>y</sup>', 'ʸ')),
    ('\<br \/\>', lambda entry: entry.lower().replace('<br />', '')),
    ('\<span class=aramaic\>', lambda entry: entry.lower().replace('<span class=aramaic>', '')),
    ('\<\/span\>', lambda entry: entry.lower().replace('</span>', '')),
    ('\<span\>', lambda entry: entry.lower().replace('<span>', '')),
)

def forwards(apps, schema_editor):
    for regex, cleaning_function in cleaners:
        dfes = DialectFeatureExample.objects.filter(example__iregex=regex)
        print('\nLooking for '+regex)
        for dfe in dfes[0:10000]:
            print(dfe)
            print('  was: ' + dfe.example[0:100])
            dfe.example = cleaning_function(dfe.example)
            print('  now: ' + dfe.example[0:100])
            dfe.save()

def backwards(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('dialects', '0013_clean_dialectfeatures_other'),
    ]

    operations = [
       migrations.RunPython(forwards, backwards),
    ]
