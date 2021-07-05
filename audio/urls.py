from django.conf.urls import url
import audio.views

app_name = 'audio'

urlpatterns = [
    url(r'^$', audio.views.AudioListView.as_view(), name='audio-list'),
    url('search', audio.views.search, name='search'),
    url(r'^(?P<pk>[0-9]+)/$', audio.views.AudioDetailView.as_view(), name='audio-detail'),
    url(r'^new$', audio.views.AudioCreateView.as_view(), name='audio-create'),
    url(r'^(?P<pk>[0-9]+)/edit$', audio.views.AudioUpdateView.as_view(), name='audio-edit'),
    url(r'^(?P<pk>[0-9]+)/transcribe$', audio.views.AudioTranscribeView.as_view(), name='audio-transcribe'),
    url(r'^(?P<pk>[0-9]+)/delete$', audio.views.AudioDeleteView.as_view(), name='audio-delete'),
]

