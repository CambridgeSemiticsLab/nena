# -*- coding: utf-8 -*-
# gENerated by Django 1.10.1 on 2016-11-29 06:25
from __future__ import unicode_literals
from __future__ import print_function

from django.apps import apps as global_apps
from django.db import migrations
from dialects.models import Dialect, DialectFeature
from grammar.models import Feature
# removed dependency in 75224e - this migration will not run without it being reinstated
# from legacy.models import GrammarFeatures

def dialect_features_forward(global_apps, schema_editor):
    for gf in GrammarFeatures.objects.all():
        try:
            d = Dialect.objects.get(pk=gf.dialect_id)
            f = Feature.objects.get(pk=gf.header_id)
            if gf.introduction is 'None':
                i = ''
            if gf.comment is None:
                c = ''
            c = gf.comment
            df = DialectFeature(
                id=gf.feature_id,
                introduction=gf.introduction,
                           comment=gf.comment,
                           dialect=d,
                           feature=f,
            ).save()
        except:
            print('not found: ', gf.__dict__)

def dialect_features_reverse(global_apps, schema_editor):
    try:
        DialectFeature.objects.filter(pk__in=[e.pk for e in GrammarFeatures.objects.all()]).delete()
    except Exception as e:
        print(e)
        pass

class Migration(migrations.Migration):

    dependencies = [
        ('dialects','0003_dialectfeature_dialectfeatureentry_dialectfeatureexample'),
        # removed dependency in 75224e - this migration will not run without it being reinstated
        # ('legacy','0001_initial'),
        ('grammar','0001_initial'),
    ]

    operations = [
        migrations.RunPython(dialect_features_forward, dialect_features_reverse),
    ]
