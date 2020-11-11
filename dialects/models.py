from django.db import models
from django.urls import reverse

from grammar.models import Feature

class Dialect(models.Model):
    CHRISTIAN = 'C'
    JEWISH = 'J'
    COMMUNITIES = (
        (CHRISTIAN ,'Christian'),
        (JEWISH, 'Jewish'),
    )
    AM = 'AM'
    IR = 'IR'
    IQ = 'IQ'
    SY = 'SY'
    TR = 'TR'
    COUNTRIES = (
        (AM, 'Armenia'),
        (IR, 'Iran'),
        (IQ, 'Iraq'),
        (SY, 'Syria'),
        (TR, 'Turkey'),
    )
    GEAM = 'GEAM'
    NEIQ = 'NEIQ'
    NWIQ = 'NWIQ'
    NWIR = 'NWIR'
    WIRN = 'WIRN'
    SETR = 'SETR'
    LOCATIONS = (
        (GEAM, 'Georgia & Armenia'),
        (NEIQ, 'NE Iraq'),
        (NWIQ, 'NW Iraq'),
        (NWIR, 'NW Iran'),
        (WIRN, 'W Iran'),
        (SETR, 'SE Turkey'),
    )
    name = models.CharField(max_length=40)
    code = models.CharField(max_length=40, blank=True, null=True)
    community = models.CharField(max_length=1, choices=COMMUNITIES,
                default='', blank=False, null=False)
    country = models.CharField(max_length=2, choices=COUNTRIES,
                default='', blank=False, null=False)
    location = models.CharField(max_length=4, choices=LOCATIONS,
                default='', blank=False, null=False)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    source = models.TextField(null=False, blank=True)
    information = models.TextField(null=False, blank=True)
    remarks = models.TextField(null=False, blank=True)

    def get_absolute_url(self):
        return reverse('dialects:dialect-detail', args=[str(self.id)])

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class DialectFeature(models.Model):
    feature   = models.ForeignKey(Feature, on_delete=models.CASCADE)
    dialect   = models.ForeignKey(Dialect, related_name='features', on_delete=models.CASCADE)
    is_absent = models.BooleanField(default=False)
    category  = models.CharField(max_length=80, null=True, blank=True)  # must match one of Feature.category_list if set
    introduction = models.TextField(null=True, blank=True)
    comment   = models.TextField(null=True, blank=True)

    def __str__(self):
        return '{} ({}): {}'.format(self.dialect, self.dialect.community, self.feature)

class DialectFeatureEntry(models.Model):
    PRIMARY = 'P'
    MARGINAL = 'M'
    FREQUENCIES = (
        (PRIMARY, 'Primary'),
        (MARGINAL, 'Marginal'),
    )
    feature = models.ForeignKey(DialectFeature, related_name='entries', on_delete=models.CASCADE)
    entry = models.CharField(max_length=160, unique=False, null=False, blank=False)
    frequency = models.CharField(max_length=1, choices=FREQUENCIES,
                default='', null=False, blank=False)
    comment = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Dialect feature entries'

    def __str__(self):
        return u"%s (%s)" % (self.feature, self.frequency)

class DialectFeatureExample(models.Model):
    feature = models.ForeignKey(DialectFeature, related_name='examples', on_delete=models.CASCADE)
    example = models.CharField(max_length=160, unique=False, null=False, blank=False)

    def __str__(self):
        return u"%s" % (self.example)
