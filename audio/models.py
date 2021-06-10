from django.db import models
from django.urls import reverse_lazy
from django.core.files.base import ContentFile
from dialects.models import Dialect

from common.storage_backends import OverwriteStorage


class Audio(models.Model):
    title = models.CharField(max_length=50, null=False)
    dialect = models.ForeignKey(Dialect, on_delete=models.CASCADE)
    description = models.CharField(max_length=255, blank=True, null=False)
    data = models.FileField(upload_to='audio/')
    annotations = models.FileField(upload_to='annotations/', null=True, blank=True)
    transcript = models.TextField(null=True, blank=True)
    translation = models.TextField(null=True, blank=True)
    nena_file = models.FileField(upload_to='nenafiles', storage=OverwriteStorage(), null=True, blank=True)
    speakers = models.CharField(max_length=200, null=True, blank=True,
                                help_text="Comma-separated list of [Initials]=[Full Name] pairs, eg. \"GK=Geoffrey Khan, CK=Cody Kingham\"")
    place = models.CharField(max_length=100, null=True, blank=True)
    transcriber = models.CharField(max_length=50, null=True, blank=True)
    source = models.CharField(max_length=200, null=True, blank=True)
    text_id = models.CharField(max_length=50, null=True, blank=True)

    def nena_compile(self):
        """ compiles the metadata and transcription into a .nena format file
            see https://github.com/CambridgeSemiticsLab/nena_corpus/blob/master/docs/nena_format.md
        """
        if not self.dialect.code:
            raise Exception("This audio's dialect {} has no `code`, please set it before compiling".format(self.dialect))

        metadata = {
            'dialect':     self.dialect.code,
            'title':       self.title,
            'encoding':    'UTF-8',
            'place':       dict(Dialect.LOCATIONS)[self.dialect.location],
            'speakers':    self.speakers,
            'transcriber': self.transcriber,
            'text_id':     self.text_id,
            'corpus_id':   self.id,
        }

        metadata_string = "\n".join(f"{key}:: {val}" for key,val in metadata.items() if val)
        filename = "{}.nena".format(self.title)
        self.nena_file.delete()
        self.nena_file.save(filename, ContentFile(metadata_string + "\n\n" + self.transcript))


    def __str__(self):
        return "{}: {}".format(self.dialect, self.title)

    def get_absolute_url(self):
        return reverse_lazy('audio:audio-list')
