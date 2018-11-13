from __future__ import unicode_literals

from django.db import models


class Dialects(models.Model):
    dialect_id = models.AutoField(primary_key=True)
    dialect = models.CharField(max_length=80)
    community = models.CharField(max_length=80, blank=True, null=True)
    country = models.CharField(max_length=160, blank=True, null=True)
    location = models.CharField(max_length=160, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    source = models.TextField(blank=True, null=True)
    information = models.TextField(blank=True, null=True)
    general_remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.dialect

    class Meta:
        managed = False
        db_table = 'dialects'
        verbose_name = 'dialect'
        verbose_name_plural = 'dialects'


class Headers(models.Model):
    header_id = models.AutoField(primary_key=True)
    header_level = models.IntegerField()
    header = models.CharField(max_length=255)
    seq_no = models.IntegerField()
    level0_seq = models.IntegerField()
    level1_seq = models.IntegerField()
    level2_seq = models.IntegerField()
    level3_seq = models.IntegerField()
    level4_seq = models.IntegerField()
    level5_seq = models.IntegerField()
    group_header = models.IntegerField()
    end_paragraph = models.IntegerField()

    def __str__(self):
        return self.header

    class Meta:
        managed = False
        db_table = 'headers'
        verbose_name = 'header'
        verbose_name_plural = 'headers'


class GrammarFeatures(models.Model):
    feature_id = models.AutoField(primary_key=True)
    introduction = models.TextField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    header = models.ForeignKey(Headers, on_delete=models.CASCADE)
    dialect = models.ForeignKey(Dialects, on_delete=models.CASCADE)

    def __str__(self):
        return "%s: %s" % (self.dialect, self.header)

    class Meta:
        managed = False
        db_table = 'grammar_features'
        verbose_name = 'grammar feature'
        verbose_name_plural = 'grammar features'


class GrammarFeatureEntries(models.Model):
    entry_id = models.AutoField(primary_key=True)
    entry = models.CharField(max_length=160)
    feature = models.ForeignKey(GrammarFeatures, on_delete=models.CASCADE)
    comment = models.TextField(blank=True, null=True)
    frequency = models.CharField(max_length=30)

    def __str__(self):
        return "%s: %s" % (self.feature, self.entry)

    class Meta:
        managed = False
        db_table = 'grammar_feature_entries'
        verbose_name = 'grammar feature entry'
        verbose_name_plural = 'grammar feature entries'


class GrammarFeatureExamples(models.Model):
    example_id = models.AutoField(primary_key=True)
    example = models.CharField(max_length=160)
    feature = models.ForeignKey(GrammarFeatures, on_delete=models.CASCADE)

    def __str__(self):
        return "%s: %s" % (self.feature.header, self.example)

    class Meta:
        managed = False
        db_table = 'grammar_feature_examples'
        verbose_name = 'grammar feature example'
        verbose_name_plural = 'grammar feature examples'


class ExtAudioMaterial(models.Model):
    ext_audio_id = models.AutoField(primary_key=True)
    dialect = models.ForeignKey(Dialects, on_delete=models.CASCADE)
    link_url = models.CharField(max_length=255)
    link_text = models.CharField(max_length=255)
    link_description = models.TextField()

    class Meta:
        managed = False
        db_table = 'ext_audio_material'


class AudioMaterial(models.Model):
    audio_id = models.AutoField(primary_key=True)
    dialect = models.ForeignKey(Dialects, on_delete=models.CASCADE)
    title = models.CharField(max_length=160)
    description = models.TextField(blank=True, null=True)
    image_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'audio_material'


class AudioFiles(models.Model):
    file_id = models.AutoField(primary_key=True)
    audio_id = models.ForeignKey(AudioMaterial, on_delete=models.CASCADE)
    transcript = models.TextField(blank=True, null=True)
    translation = models.TextField(blank=True, null=True)
    filename = models.CharField(max_length=160, blank=True, null=True)
    filesize = models.CharField(max_length=50, blank=True, null=True)
    filetype = models.CharField(max_length=50, blank=True, null=True)
    audio_url = models.CharField(max_length=255, blank=True, null=True)
    audio_link = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'audio_files'


class Dialectmaps(models.Model):
    map_id = models.AutoField(primary_key=True)
    map_title = models.CharField(max_length=80)
    map_notes = models.CharField(max_length=255, blank=True, null=True)
    map_author = models.CharField(max_length=80, blank=True, null=True)
    map_savedate = models.DateField()
    map_strdata = models.TextField()
    map_postdata = models.TextField()

    class Meta:
        managed = False
        db_table = 'dialectmaps'


class Images(models.Model):
    image_id = models.AutoField(primary_key=True)
    dialect_id = models.ForeignKey(Dialects, on_delete=models.CASCADE)
    image = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    caption = models.CharField(max_length=255)
    tags = models.CharField(max_length=255, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    source = models.CharField(max_length=255, blank=True, null=True)
    date_created = models.DateField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    date_added = models.DateField()

    class Meta:
        managed = False
        db_table = 'images'


class Images2(models.Model):
    image_id = models.AutoField(primary_key=True)
    dialect_id = models.ForeignKey(Dialects, on_delete=models.CASCADE)
    image = models.CharField(max_length=255)
    image_small = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    source = models.CharField(max_length=255)
    date_created = models.DateField()

    class Meta:
        managed = False
        db_table = 'images2'


class Imagestest(models.Model):
    image_id = models.AutoField(primary_key=True)
    dialect_id = models.ForeignKey(Dialects, on_delete=models.CASCADE)
    image = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    caption = models.CharField(max_length=255)
    notes = models.TextField(blank=True, null=True)
    source = models.CharField(max_length=255, blank=True, null=True)
    date_created = models.DateField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    date_added = models.DateField()

    class Meta:
        managed = False
        db_table = 'imagestest'


class Introduction(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=100)
    introdata = models.TextField()
    photo = models.CharField(max_length=100, blank=True, null=True)
    caption = models.CharField(max_length=100, blank=True, null=True)
    publishdate = models.DateField()

    class Meta:
        managed = False
        db_table = 'introduction'


class News(models.Model):
    news_id = models.AutoField(primary_key=True)
    news_type = models.CharField(max_length=80)
    title = models.CharField(max_length=80)
    short_description = models.CharField(max_length=255)
    news = models.TextField(blank=True, null=True)
    link = models.CharField(max_length=255, blank=True, null=True)
    publish_date = models.DateField()
    expiry_date = models.DateField()

    class Meta:
        managed = False
        db_table = 'news'


class Researchteam(models.Model):
    rtid = models.AutoField(primary_key=True)
    listposition = models.IntegerField()
    rtname = models.CharField(max_length=50)
    rttype = models.CharField(max_length=50)
    rtposition = models.CharField(max_length=100, blank=True, null=True)
    rtaddress = models.CharField(max_length=100, blank=True, null=True)
    rtemail = models.CharField(max_length=25, blank=True, null=True)
    rtphone = models.CharField(max_length=25, blank=True, null=True)
    rtphoto = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'researchteam'


class Sitehelp(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=100)
    shdata = models.TextField()
    photo = models.CharField(max_length=100, blank=True, null=True)
    caption = models.CharField(max_length=100, blank=True, null=True)
    publishdate = models.DateField()

    class Meta:
        managed = False
        db_table = 'sitehelp'
