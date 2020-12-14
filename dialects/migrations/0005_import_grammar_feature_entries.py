# -*- coding: utf-8 -*-
# gENerated by Django 1.10.1 on 2016-11-29 06:25
from __future__ import unicode_literals
from __future__ import print_function

from django.apps import apps as global_apps
from django.db import migrations
from dialects.models import Dialect, DialectFeature, DialectFeatureEntry
from grammar.models import Feature
# removed dependency in 75224e - this migration will not run without it being reinstated
# from legacy.models import GrammarFeatures, GrammarFeatureEntries

def dialect_feature_entries_forward(global_apps, schema_editor):
    for gf in GrammarFeatureEntries.objects.all():
        try:
            f = DialectFeature.objects.get(pk=gf.feature_id)
            if gf.frequency == "Primary":
                fr = DialectFeatureEntry.PRIMARY
            else:
                fr = DialectFeatureEntry.MARGINAL
            df = DialectFeatureEntry(
                id=gf.entry_id,
                feature=f,
                entry=gf.entry,
                frequency=fr,
                comment=gf.comment,
            ).save()
        except:
            print('no feature: ', gf.entry_id)

def dialect_feature_entries_reverse(global_apps, schema_editor):
    try:
        DialectFeatureEntry.objects.filter(pk__in=[e.pk for e in GrammarFeatureEntries.objects.all()]).delete()
    except Exception as e:
        print(e)
        pass

class Migration(migrations.Migration):

    dependencies = [
        ('dialects','0004_import_grammar_features'),
        # removed dependency in 75224e - this migration will not run without it being reinstated
        # ('legacy','0001_initial'),
        ('grammar','0001_initial'),
    ]

    operations = [
        migrations.RunPython(dialect_feature_entries_forward, dialect_feature_entries_reverse),
    ]
