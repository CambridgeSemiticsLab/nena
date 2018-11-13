from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.db.models import Q
from django.http import JsonResponse

from dialectmaps.models import DialectMap, MapGroup, MapItem

class DialectMapListView(ListView):
    model = DialectMap
    name = 'Dialect maps'
    context_object_name = 'maps'

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return DialectMap.objects.filter(Q(author=self.request.user) | Q(public=True))
        else:
            return DialectMap.objects.filter(public=True)

    def get_context_data(self, **kwargs):
        context = super(DialectMapListView, self).get_context_data(**kwargs)
        return context

class DialectMapDetailView(DetailView):
    model = DialectMap
    name = 'Dialect map'
    context_object_name = 'dialectmap'

    def get_context_data(self, **kwargs):
        context = super(DialectMapDetailView, self).get_context_data(**kwargs)
        return context

class DialectMapListJSONView(ListView):
    pass

class DialectMapDetailJSONView(DetailView):

    model = DialectMap

    def get_context_data(self, **kwargs):
        context = super(DialectMapDetailJSONView, self).get_context_data(**kwargs)
        context['groups'] = MapGroup.objects.filter(dialectmap=self.kwargs['pk'])
        context['items'] = MapItem.objects.filter(group__in=context['groups'])
        return context

    def render_to_response(self, context):
        data = {'type': 'FeatureCollection'}
        features = []
        for d in context['items']:
            if d.entry.feature.dialect.latitude and d.entry.feature.dialect.longitude:
                features.append({"id": d.pk, "type": "Feature", "geometry": {"type": "Point", "coordinates": [d.entry.feature.dialect.longitude, d.entry.feature.dialect.latitude]}, "properties": {"name": d.entry.entry,  "class": d.group.label}}) 
        data['features'] = features
        return JsonResponse(data)
        
