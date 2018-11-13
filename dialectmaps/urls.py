from django.conf.urls import url

import dialectmaps.views

app_name = 'dialectmaps'

urlpatterns = [
    url(r'^$', dialectmaps.views.DialectMapListView.as_view(), name='dialectmap-list'),
    url(r'^(?P<pk>[0-9]+)/$', dialectmaps.views.DialectMapDetailView.as_view(), name='dialectmap-detail'),
]
