from django.contrib import admin

from .models import DialectMap, MapGroup, MapItem

admin.site.register(DialectMap)
admin.site.register(MapGroup)
admin.site.register(MapItem)
