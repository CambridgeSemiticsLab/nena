from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from . import views

app_name = 'grammar'

urlpatterns = [
    url(r'^$', views.features, name='feature-list'),
    url(r'^(?P<section>[0-9\.]+)$', views.features, name='feature-list-section'),
    url(r'^features/(?P<pk>[0-9]+)$', views.dialects_with_feature, name='feature-detail'),
    url(r'^features/(?P<pk>[0-9]+)/map$', views.map_of_feature, name='feature-map'),
    url(r'^(?P<pk>[0-9]+)/paradigm$', login_required(views.FeatureParadigmView.as_view()), name='feature-paradigm'),

]
