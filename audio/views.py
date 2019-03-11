from django.shortcuts import get_object_or_404

from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import reverse_lazy

from audio.models import Audio
from dialects.models import Dialect


class AudioListView(ListView):

    name = 'Audio'
    model = Audio
    context_object_name = 'clips'

    def get_context_data(self, **kwargs):
        context = super(AudioListView, self).get_context_data(**kwargs)
        return context

class AudioDetailView(DetailView):

    name = 'Audio'
    model = Audio
    context_object_name = 'clip'

    def get_context_data(self, **kwargs):
        context = super(AudioDetailView, self).get_context_data(**kwargs)
        return context

class DialectAudioView(ListView):

    name = 'Audio'
    context_object_name = 'clips'

    def get_queryset(self):
        self.dialect = get_object_or_404(Dialect, pk=self.kwargs['dialect'])
        return Audio.objects.filter(dialect=self.dialect)

    def get_context_data(self, **kwargs):
        context = super(DialectAudioView, self).get_context_data(**kwargs)
        context['dialect'] = self.dialect
        return context

@method_decorator(login_required, name='dispatch')
class AudioCreateView(CreateView):
    model = Audio
    fields = '__all__'

@method_decorator(login_required, name='dispatch')
class AudioUpdateView(UpdateView):
    model = Audio
    fields = '__all__'

@method_decorator(login_required, name='dispatch')
class AudioDeleteView(DeleteView):
    model = Audio
    fields = '__all__'
    success_url = reverse_lazy('audio:audio-list')

