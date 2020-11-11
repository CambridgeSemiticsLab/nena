from django.db import models
from django.urls import reverse_lazy
from dialects.models import Dialect

class Audio(models.Model):
    title = models.CharField(max_length=50, null=False)
    dialect = models.ForeignKey(Dialect, on_delete=models.CASCADE)
    description = models.CharField(max_length=255, blank=True, null=False)
    data = models.FileField(upload_to='audio/')
    annotations = models.FileField(upload_to='annotations/', null=True, blank=True)
    transcript = models.TextField(null=True, blank=True)
    translation = models.TextField(null=True, blank=True)
    speakers = models.CharField(max_length=200, null=True, blank=True,
                                help_text="Comma-separated list of [Initials]=[Full Name] pairs, eg. \"GK=Geoffrey Khan, CK=Cody Kingham\"")
    place = models.CharField(max_length=100, null=True, blank=True)
    transcriber = models.CharField(max_length=50, null=True, blank=True)
    source = models.CharField(max_length=200, null=True, blank=True)
    text_id = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return "{}: {}".format(self.dialect, self.title)

    def get_absolute_url(self):
        return reverse_lazy('audio:audio-list')
