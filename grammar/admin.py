from django.contrib import admin

from .models import Feature
from django.contrib import admin
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory

class FeatureAdmin(TreeAdmin):
    readonly_fields=('depth', 'fullheading')
    form = movenodeform_factory(Feature)

admin.site.register(Feature, FeatureAdmin)
#admin.site.register(DialectFeature)
#admin.site.register(DialectFeatureEntry)
#admin.site.register(DialectFeatureExample)
