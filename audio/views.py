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


class AudioDetailView(DetailView):
    name = 'Audio'
    model = Audio
    context_object_name = 'clip'

    def get_context_data(self, **kwargs):
        context = super(AudioDetailView, self).get_context_data(**kwargs)
        clip = context['clip']
        regex = '(\(\d+(?:@\d+:\d+)?\))'
        transcript_chunks = re.split(regex, clip.transcript or '')
        if len(transcript_chunks) > 1:
            translation_chunks = re.split(regex, clip.translation or '')
            text_chunks = zip(transcript_chunks[1::2], transcript_chunks[2::2], translation_chunks[2::2])
        else:
            text_chunks = None

        # todo - try to find matching words within text
        # words = set(re.findall('\w+', clip.transcript))
        # words = [w for w in words if not w.isdigit()]

        # dfs = DialectFeatureEntry.objects.filter(feature__dialect_id=clip.dialect_id) \
                                         # .filter(entry__in=words) \
                                         # .values_list('entry', 'feature__dialect_id')

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
    fields = '__all__'

    def get_success_url(self):
        return reverse('audio:audio-detail', args=(self.object.pk,))


@method_decorator(login_required, name='dispatch')
class AudioUpdateView(UpdateView):
    model = Audio
    fields = '__all__'

    def get_success_url(self):
        return reverse('audio:audio-detail', args=(self.kwargs['pk'],))


@method_decorator(login_required, name='dispatch')
class AudioDeleteView(DeleteView):
    model = Audio
    fields = '__all__'
    success_url = reverse_lazy('audio:audio-list')

