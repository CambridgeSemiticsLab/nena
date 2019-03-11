from django.db import models
from django.urls import reverse_lazy
from imagekit.models import ImageSpecField
from imagekit.processors import Crop, Thumbnail

from dialects.models import Dialect

class Photo(models.Model):
    title = models.CharField(max_length=50, null=False)
    dialect = models.ForeignKey(Dialect, on_delete=models.CASCADE)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    description = models.CharField(max_length=255, blank=True, null=False)
    original_image = models.ImageField(upload_to='photos')
    thumbnail = ImageSpecField([Thumbnail(80, 60)], source='original_image')

    def __str__(self):
        return "{:s}: {:s}".format(self.dialect.name, self.title)

    def get_absolute_url(self):
        return reverse_lazy('gallery:photo-list')
