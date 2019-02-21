from django.conf.urls import url
from django.contrib.admin.views.decorators import staff_member_required

from . import views

app_name = 'grammar'

urlpatterns = [
    url(r'^$', staff_member_required(views.FeatureListView.as_view()), name='feature-list'),
    url(r'^(?P<pk>[0-9]+)$', views.dialects_with_feature, name='feature-detail'),
    url(r'^(?P<pk>[0-9]+)/paradigm$', staff_member_required(views.FeatureParadigmView.as_view()), name='feature-paradigm'),

]
