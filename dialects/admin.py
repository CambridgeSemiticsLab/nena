from django.contrib import admin

from .models import DialectGroup, Dialect, DialectFeature, DialectFeatureEntry, DialectFeatureExample

admin.site.register(DialectGroup)
admin.site.register(Dialect)
admin.site.register(DialectFeature)
admin.site.register(DialectFeatureEntry)
admin.site.register(DialectFeatureExample)
