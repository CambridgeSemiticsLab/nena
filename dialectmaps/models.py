from django.conf import settings
from django.db import models

from dialects.models import DialectFeature, DialectFeatureEntry

class DialectMap(models.Model):
    name = models.CharField(max_length=120, unique=False, blank=True, null=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    public = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class MapGroup(models.Model):
    dialectmap = models.ForeignKey(DialectMap, on_delete=models.CASCADE)
    label = models.CharField(max_length=40, unique=False, blank=True, null=True)

    def __str__(self):
        return '{}: {}'.format(self.dialectmap.name, self.label)

class MapItem(models.Model):
    group = models.ForeignKey(MapGroup, on_delete=models.CASCADE)
    entry = models.ForeignKey(DialectFeatureEntry, on_delete=models.CASCADE)

    def __str__(self):
        return self.entry.entry

