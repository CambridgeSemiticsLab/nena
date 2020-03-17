import re

from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import reverse_lazy

from audio.models import Audio
from dialects.models import Dialect, DialectFeatureEntry


class AudioListView(ListView):
    name = 'Audio'
    model = Audio
    context_object_name = 'clips'

    def get_queryset(self):
        return Audio.objects.all().values('id', 'title', 'transcript', 'translation',
                                          'dialect__id', 'dialect__name') \
                                  .order_by('dialect__name', 'title')


def chunk_translation_text(audio):
    """ takes an Audio model and returns a (timestamp, transcription_chunk, translation_chunk) list
    """
    regex = '(\(\d+(?:@\d+:\d\d)?\))?'
    transcript_chunks = re.split(regex, audio.transcript or '')
    if len(transcript_chunks) > 1:
        translation_chunks = re.split(regex, audio.translation or '')
        text_chunks = zip(transcript_chunks[1::2], transcript_chunks[2::2], translation_chunks[2::2])
    else:
        text_chunks = (('(1@0:00)', audio.transcript, audio.translation),)

    text_chunks = [[x.rstrip(')').lstrip('(0123456789').lstrip('@'),y,z] for x,y,z in text_chunks]

    text_chunks[0][0] = text_chunks[0][0] or '0:00'

    return text_chunks


class AudioDetailView(DetailView):
    name = 'Audio'
    model = Audio
    context_object_name = 'clip'
    template_name = 'audio/audio_transcribe.html'

    def get_context_data(self, **kwargs):
        context = super(AudioDetailView, self).get_context_data(**kwargs)

        # todo - try to find matching words within text
        # words = set(re.findall('\w+', clip.transcript))
        # words = [w for w in words if not w.isdigit()]

        # dfs = DialectFeatureEntry.objects.filter(feature__dialect_id=clip.dialect_id) \
                                         # .filter(entry__in=words) \
                                         # .values_list('entry', 'feature__dialect_id')
        text_chunks = chunk_translation_text(context['clip'])
        context.update({'text_chunks': text_chunks})
        return context


class DialectAudioView(AudioListView):

    def get_queryset(self):
        self.dialect = get_object_or_404(Dialect, pk=self.kwargs['dialect'])
        return super(DialectAudioView, self).get_queryset().filter(dialect=self.dialect)

    def get_context_data(self, **kwargs):
        context = super(DialectAudioView, self).get_context_data(**kwargs)
        context['dialect'] = self.dialect
        return context


@method_decorator(login_required, name='dispatch')
class AudioCreateView(CreateView):
    model = Audio
    fields = ('title', 'dialect', 'description', 'data')

    def get_success_url(self):
        return reverse('audio:audio-detail', args=(self.object.pk,))


@method_decorator(login_required, name='dispatch')
class AudioUpdateView(UpdateView):
    model = Audio
    fields = ('title', 'dialect', 'description', 'data')

    def get_success_url(self):
        return reverse('audio:audio-detail', args=(self.kwargs['pk'],))


@method_decorator(login_required, name='dispatch')
class AudioTranscribeView(AudioUpdateView):
    template_name = 'audio/audio_transcribe.html'
    fields = ('transcript', 'translation')
    context_object_name = 'clip'

    def get_context_data(self, **kwargs):
        context     = super(AudioUpdateView, self).get_context_data(**kwargs)
        text_chunks = chunk_translation_text(context['clip'])
        context.update({'text_chunks': text_chunks})
        return context


@method_decorator(login_required, name='dispatch')
class AudioDeleteView(DeleteView):
    model = Audio
    fields = '__all__'
    success_url = reverse_lazy('audio:audio-list')

