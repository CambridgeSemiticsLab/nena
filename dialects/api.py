from django.conf.urls import url

from dialects.views import DialectListJSONView, DialectDetailJSONView

app_name = "api-dialects"

urlpatterns = [
    url(r'^$', DialectListJSONView.as_view(), name='dialect-api-list'),
    url(r'^(?P<pk>[0-9]+)/$', DialectDetailJSONView.as_view(), name='dialect-api-detail'),

]
