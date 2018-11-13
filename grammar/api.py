from django.conf.urls import url

from grammar.views import FeatureListJSONView

app_name = 'api-grammar'

urlpatterns = [
    url(r'^$', FeatureListJSONView.as_view(), name='feature-api-list'),
    #url(r'^(?P<pk>[0-9]+)/$', DialectDetailJSONView.as_view(), name='dialect-api-detail'),

]
