from django.db import models
from django.urls import reverse_lazy
from dialects.models import Dialect
from ckeditor.fields import RichTextField

class Audio(models.Model):
    title = models.CharField(max_length=50, null=False)
    dialect = models.ForeignKey(Dialect, on_delete=models.CASCADE)
    description = models.CharField(max_length=255, blank=True, null=False)
    data = models.FileField(upload_to='media/')
    annotations = models.FileField(upload_to='media/annotations/',  null=True, blank=True)
    transcript = RichTextField(null=True, blank=True)
    translation = RichTextField(null=True, blank=True)

    def __str__(self):
        return "{}: {}".format(self.dialect, self.title)

    def get_absolute_url(self):
        return reverse_lazy('audio:audio-list')
