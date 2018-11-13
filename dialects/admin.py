from django.contrib import admin

from .models import Dialect, DialectFeature, DialectFeatureEntry, DialectFeatureExample

admin.site.register(Dialect)
admin.site.register(DialectFeature)
admin.site.register(DialectFeatureEntry)
admin.site.register(DialectFeatureExample)
