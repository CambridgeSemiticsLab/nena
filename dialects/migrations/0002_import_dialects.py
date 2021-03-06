# -*- coding: utf-8 -*-
# gENerated by Django 1.10.1 on 2016-11-29 06:25
from __future__ import unicode_literals

from django.apps import apps as global_apps
from django.db import migrations
from dialects.models import Dialect

from ftfy import fix_text
from ftfy.fixes import unescape_html, decode_escapes

from common.utils import fixup, enum

def dialect_forward(global_apps, schema_editor):
    COMMUNITIES = {
        'Christian': 'C',
        'Jewish': 'J',
    }
    COUNTRIES = {
        'Armenia': 'AM',
        'Iran': 'IR',
        'Iraq': 'IQ',
        'Syria': 'SY',
        'Turkey': 'TR',
    }
    LOCATIONS = {
        'Georgia & Armenia': 'GEAM',
        'NE Iraq': 'NEIQ',
        'NW Iraq': 'NWIQ',
        'NW Iran': 'NWIR',
        'W Iran': 'WIRN',
        'SE Turkey': 'SETR',
    }
    try:
        OldModel = global_apps.get_model('legacy', 'Dialects')
    except Exception as e:
        # The old app isn't installed.
        print(' old app not found, skipping migrationi:', e)
        return

    NewModel = global_apps.get_model('dialects', 'Dialect')

    for id in [e.pk for e in OldModel.objects.all()]: # using legacy
        try:
            obj = OldModel.objects.get(pk=id) # using legacy
            new_obj = NewModel(id=obj.dialect_id, name=fixup(obj.dialect), latitude=obj.latitude, longitude=obj.longitude)
            new_obj.community = enum(obj.community, COMMUNITIES)
            new_obj.country = enum(obj.country, COUNTRIES)
            new_obj.location = enum(obj.location, LOCATIONS)
            new_obj.source = fixup(obj.source) if obj.source is not None else ''
            new_obj.information = fixup(obj.information) if obj.information is not None else ''
            new_obj.remarks = fixup(obj.general_remarks) if obj.general_remarks is not None else ''

            new_obj.save() # using default
        except OldModel.DoesNotExist:
            pass

def dialect_reverse(global_apps, schema_editor):
    OldModel = global_apps.get_model('legacy', 'Dialects')
    NewModel = global_apps.get_model('dialects', 'Dialect')
    try:
        NewModel.objects.filter(pk__in=[e.pk for e in OldModel.objects.all()]).delete()
    except Exception as e:
        print(e)
        pass


class Migration(migrations.Migration):

    dependencies = [
        ('dialects','0001_initial'),
        # removed dependency in 75224e - this migration will not run without it being reinstated
        # ('legacy','0001_initial'),
    ]

    operations = [
        migrations.RunPython(dialect_forward, dialect_reverse),
    ]
