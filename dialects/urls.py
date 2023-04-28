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
    url(r'^(?P<dialect_id_string>[0-9,]+)/grammar$', dialects.views.features_of_dialect, name='dialect-grammar'),
    url(r'^(?P<dialect_id_string>[0-9,]+)/setup-comparison$', dialects.views.setup_comparison, name='setup-comparison'),
    url(r'^(?P<dialect_id_string>[0-9,]+)/grammar/(?P<section>[0-9\.]+)$', dialects.views.features_of_dialect, name='dialect-grammar-section'),
    url(r'download-entries-in-(?P<section>[0-9\.]+)?$', dialects.views.download_feature_entries, name='download-feature-entries'),
    url(r'^(?P<dialect>[0-9]+)/feature/(?P<pk>[0-9]+)$', dialects.views.DialectFeatureDetailView.as_view(), name='dialect-feature'),
    # todo make dialect-feature use dialect_id and feature_heading consistent with below
    url(r'^(?P<dialect_id>[0-9]+)/feature/(?P<feature_heading>[0-9\.]+)/edit$', dialects.views.dialect_feature_edit, name='dialect-feature-edit'),
    url(r'^(?P<dialect_id>[0-9]+)/feature/(?P<feature_heading>[0-9\.]+)/pane$', dialects.views.dialect_feature_pane, name='dialect-feature-pane'),
    url(r'^(?P<dialect>[0-9]+)/gallery$', gallery.views.DialectPhotoView.as_view(), name='dialect-gallery'),
    url(r'^(?P<dialect>[0-9]+)/audio$', audio.views.DialectAudioView.as_view(), name='dialect-audio'),
    url('build-dialects-json', dialects.views.build_dialects_json, name='build_dialects_json'),
    url('problems', dialects.views.problems, name='problems'),
]
