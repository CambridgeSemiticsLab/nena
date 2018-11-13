from django.conf.urls import url
import gallery.views

app_name = 'gallery'

urlpatterns = [
    url(r'^$', gallery.views.PhotoListView.as_view(), name='photo-list'),
    url(r'^(?P<pk>[0-9]+)/$', gallery.views.PhotoDetailView.as_view(),
        name='photo-detail'),
    url(r'^new$', gallery.views.PhotoCreateView.as_view(), name='photo-create'),
    url(r'^(?P<pk>[0-9]+)/edit$', gallery.views.PhotoUpdateView.as_view(), name='photo-edit'),
    url(r'^(?P<pk>[0-9]+)/delete$', gallery.views.PhotoDeleteView.as_view(), name='photo-delete'),
]

