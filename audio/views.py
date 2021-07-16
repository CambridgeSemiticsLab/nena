import re
import json
from itertools import zip_longest
from io import StringIO
import sys

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, Http404, JsonResponse
from django.urls import reverse
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import reverse_lazy
from django.db.models import F
from django.contrib import messages
from django.conf import settings

from audio.models import Audio
from dialects.models import Dialect, DialectFeatureEntry


class AudioListView(ListView):
    name = 'Audio'
    model = Audio
    context_object_name = 'clips'

    def get_queryset(self):
        return Audio.objects.all().values('id', 'title', 'source', 'text_id', 'transcript', 'translation',
                                          'dialect__id', 'dialect__name') \
                                  .order_by('dialect__name', F('text_id').asc(nulls_last=True), 'title')


def chunk_translation_text(audio):
    """ takes an Audio model and returns a (metadata, transcription_chunk, translation_chunk) list
    """
    # This will match any term in round brackets which starts with 2/3 capital letters, or a number, or an @ symbol
    # it will also match empty round brackets, so: "()", "(GK ...)", "(12 ...)", "(1:23 ...)", "(@1:23 ...)"
    regex = '(\((?:[A-Z]{2,3}.*?|[0-9@]+.*?|)\))'
    transcript_chunks = re.split(regex, audio.transcript or '')
    if len(transcript_chunks) > 1:
        # if transcript_chunks[0] == '':
            # transcrip_chunks = transcript_chunks[1:]
        translation_chunks = re.split(regex, audio.translation or '')
        text_chunks = zip_longest(transcript_chunks[1::2], transcript_chunks[2::2], translation_chunks[2::2],
                                  fillvalue='')
    else:
        text_chunks = (('(0:00)', audio.transcript or '', audio.translation or ''),)

    def parse_metadata(raw_string):
        section_number_match = re.search('(?<=[ \(])\d+(?=[ \)])', raw_string)
        section_number = section_number_match.group(0) if section_number_match else ''

        timestamp_match = re.search('(?<=[ @\(])\d+:\d{2}(?=[ \)])', raw_string)
        timestamp = timestamp_match.group(0) if timestamp_match else ''

        speaker_match = re.search('(?<=[ \(])[A-Z]{2,4}(?=[ \)])', raw_string)
        speaker = speaker_match.group(0) if speaker_match else ''

        return {'section_number': section_number, 'timestamp': timestamp, 'speaker': speaker}

    text_chunks = [[parse_metadata(x), y.strip(), z.strip()] for x,y,z in text_chunks]

    if text_chunks[0][1] == '' and len(text_chunks) > 1:
        text_chunks = text_chunks[1:]

    if not text_chunks[0][0]['timestamp']:
        text_chunks[0][0]['timestamp'] = '0:00'

    return text_chunks


class AudioDetailView(DetailView):
    name = 'Audio'
    model = Audio
    context_object_name = 'clip'
    template_name = 'audio/audio_transcribe.html'

    def present_text(self, chunks):
        superscript_languages = lambda text : re.sub(r"\<(\w+):(.+?)\>", r"<sup>\1</sup>\2<sup>\1</sup>", text)
        return ((x,superscript_languages(y),z) for x,y,z in chunks)

    def get_context_data(self, **kwargs):
        context = super(AudioDetailView, self).get_context_data(**kwargs)
        text_chunks = chunk_translation_text(context['clip'])
        context.update({'text_chunks': self.present_text(text_chunks)})
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
    fields = ('transcript', 'translation', 'speakers', 'place', 'transcriber', 'source', 'text_id')
    context_object_name = 'clip'

    def get_success_url(self):
        return reverse('audio:audio-transcribe', args=(self.kwargs['pk'],))

    def get_context_data(self, **kwargs):
        context     = super(AudioUpdateView, self).get_context_data(**kwargs)
        text_chunks = chunk_translation_text(context['clip'])
        context.update({
            'text_chunks': text_chunks,
            'inline_fields': (context['form'][f] for f in ('transcriber', 'source', 'text_id', 'speakers', 'place'))
            })
        return context


@login_required
def search(request):
    output = ''
    text_issues = []

    if request.method == "POST":
        audios = Audio.objects.filter(transcript__isnull=False)
        num_transcripts = audios.count()
        audios = audios.filter(dialect__code__isnull=False)
        num_complete = audios.count()
        for audio in audios:
            audio.nena_compile()
            pass
        output += "{} of {} corpus entries compiled to .nena format \n".format(num_complete, num_transcripts)

        # from https://stackoverflow.com/questions/1218933/can-i-redirect-the-stdout-into-some-sort-of-string-buffer
        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()

        sys.path.append(str(settings.BASE_DIR.path('nena-pipeline')))
        from pipeline.corpus_pipeline import CorpusPipeline
        cp = CorpusPipeline(str(settings.BASE_DIR.path('nena-pipeline/config.json')))
        try:
            cp.build_corpus(settings.MEDIA_ROOT + '/nenafiles', settings.MEDIA_ROOT + '/nenapipelinefiles')

            """ The CorpusPipeline returns a dict of errors keyed by pipeline stage name
                Each key returns a list of strings, one per error, eg:
            {
              "nena_parser": [
                "corpus_id 15: Illegal character '<' @ index 107",
                ...
                "corpus_id 210: unexpected PUNCT_END (',') at index 1295",
              ],
              "tf_builder": []
            }
            """

            output += json.dumps(cp.errors, indent=2)
            import re
            for error_string in cp.errors.get('nena_parser', []):
                matches = re.match(r"^corpus_id (\d+): (.+)$", error_string)
                text_issues.append(matches.groups())
        except Exception:
            print(json.dumps(cp.errors, indent=2))

        sys.stdout = old_stdout
        output += mystdout.getvalue()

    context = {
        'output': output,
        'text_issues': text_issues,
        }
    return render(request, 'audio/search.html', context)


@method_decorator(login_required, name='dispatch')
class AudioDeleteView(DeleteView):
    model = Audio
    fields = '__all__'
    success_url = reverse_lazy('audio:audio-list')

