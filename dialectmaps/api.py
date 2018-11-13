from django.conf.urls import url

from dialectmaps.views import DialectMapListJSONView, DialectMapDetailJSONView

app_name = 'api-dialectmaps'

urlpatterns = [
    url(r'^$', DialectMapListJSONView.as_view(), name='dialectmap-api-list'),
    url(r'^(?P<pk>[0-9]+)/$', DialectMapDetailJSONView.as_view(), name='dialectmap-api-detail'),

]
