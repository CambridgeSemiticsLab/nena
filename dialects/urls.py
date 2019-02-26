from django.conf.urls import url
from django.contrib.admin.views.decorators import staff_member_required

import dialects.views
import gallery.views
import audio.views

app_name = 'dialects'

urlpatterns = [
    url(r'^$', dialects.views.DialectListView.as_view(), name='dialect-list'),
    url(r'^(?P<pk>[0-9]+)/$', dialects.views.DialectDetailView.as_view(), name='dialect-detail'),
    url(r'^new/$', staff_member_required(dialects.views.DialectCreateView.as_view()), name='dialect-new'),
    url(r'^(?P<pk>[0-9]+)/edit/$', staff_member_required(dialects.views.DialectUpdateView.as_view()), name='dialect-edit'),
    url(r'^(?P<pk>[0-9]+)/delete/$', staff_member_required(dialects.views.DialectDeleteView.as_view()), name='dialect-delete'),
    url(r'^(?P<dialect_id>[0-9]+)/grammar$', dialects.views.features_of_dialect, name='dialect-grammar'),
    url(r'^(?P<dialect_id>[0-9]+)/grammar/(?P<section>[0-9\.]+)$', dialects.views.features_of_dialect, name='dialect-grammar-section'),
    url(r'^(?P<dialect>[0-9]+)/feature/(?P<pk>[0-9]+)$', dialects.views.DialectFeatureDetailView.as_view(), name='dialect-feature'),
    url(r'^(?P<dialect>[0-9]+)/gallery$', gallery.views.DialectPhotoView.as_view(), name='dialect-gallery'),
    url(r'^(?P<dialect>[0-9]+)/audio$', audio.views.DialectAudioView.as_view(), name='dialect-audio'),
    url('problems', dialects.views.problems, name='problems'),
]
