from django.conf.urls import url
from django.contrib.admin.views.decorators import staff_member_required

import grammar.views

app_name = 'grammar'

urlpatterns = [
    url(r'^$', staff_member_required(grammar.views.FeatureListView.as_view()), name='feature-list'),
    url(r'^(?P<pk>[0-9]+)/$', staff_member_required(grammar.views.FeatureDetailView.as_view()), name='feature-detail'),
    url(r'^(?P<pk>[0-9]+)/paradigm$', staff_member_required(grammar.views.FeatureParadigmView.as_view()), name='feature-paradigm'),

]
