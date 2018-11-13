from django.shortcuts import render
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator

from django.shortcuts import get_object_or_404

from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from dialects.models import Dialect, DialectFeature
from grammar.models import Feature

class DialectListView(ListView):

    name = 'Dialects'
    model = Dialect
    # paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super(DialectListView, self).get_context_data(**kwargs)
        return context

class DialectDetailView(DetailView):

    name = 'Dialect details'
    model = Dialect

    def get_context_data(self, **kwargs):
        context = super(DialectDetailView, self).get_context_data(**kwargs)
        return context

class DialectListJSONView(ListView):

    name = 'Dialects'
    model = Dialect

    def get_context_data(self, **kwargs):
        context = super(DialectListJSONView, self).get_context_data(**kwargs)
        return context

    def render_to_response(self, context):
        data = {'type': 'FeatureCollection', 'features': []}
        for d in context['object_list']:
            if d.latitude and d.longitude:
                data['features'].append({"id": d.pk, "type": "Feature", "geometry": {"type": "Point", "coordinates": [d.longitude, d.latitude]}, "properties": {"name": d.name, "community": d.community, "url": d.get_absolute_url(), "class": "group1" if d.community == "C"  else "group2"}})
        return JsonResponse(data, safe=False)

class DialectDetailJSONView(DetailView):
    name = 'Dialects'
    model = Dialect

    def get_context_data(self, **kwargs):
        context = super(DialectDetailJSONView, self).get_context_data(**kwargs)
        return context

    def render_to_response(self, context):
        for d in [context['dialect']]:
            data = {"id": d.pk, "type": "Feature", "geometry": {"type": "Point", "coordinates": [d.longitude, d.latitude]}, "properties": {"name": d.name, "community": d.community, "url": d.get_absolute_url(), "class": "group1" if d.community == "C"  else "group2"}}
            return JsonResponse(data, safe=False)

class DialectCreateView(CreateView):
    model = Dialect
    fields = ['name', 'community', 'country', 'location', 'latitude', 'longitude', 'source', 'information', 'remarks'] 

class DialectUpdateView(UpdateView):
    model = Dialect
    fields = ['name', 'community', 'country', 'location', 'latitude', 'longitude', 'source', 'information', 'remarks']
#    template_name_suffix = '_update_form'

class DialectDeleteView(DeleteView):
    model = Dialect
    success_url = reverse_lazy('dialects:dialect-list')

class DialectFeatureListView(ListView):

    name = 'Grammatical features'
    context_object_name = 'features'

    def features_by_dialect_feature(dialect):
        # d = Dialect.objects.get(dialect)
        df = DialectFeature.objects.filter(dialect=dialect)
        gf = Feature.objects.in_bulk(df)

    def get_queryset(self):
        self.dialect = get_object_or_404(Dialect, pk=self.kwargs['dialect'])
        return DialectFeature.objects.filter(dialect=self.dialect)

    def get_context_data(self, **kwargs):
        context = super(DialectFeatureListView, self).get_context_data(**kwargs)
        context['dialect'] = self.dialect
        context['grammar_features'] = Feature.objects.all()
        context['pks'] = set()
        for f in context['features']:
            for h in f.feature.get_ancestors():
                context['pks'].add(h.pk)
        return context

class DialectFeatureDetailView(DetailView):

    name = 'DialectFeatureDetail'
    model = DialectFeature

    def get_context_data(self, **kwargs):
        context = super(DialectFeatureDetailView, self).get_context_data(**kwargs)
        return context

