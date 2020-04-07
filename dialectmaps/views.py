import json

from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.db.models import Q, F
from django.http import JsonResponse
from django.urls import reverse_lazy, reverse

from dialects.models import Dialect
from dialectmaps.models import DialectMap, MapGroup, MapItem, DialectFeatureEntry
from dialects.views import object_to_map_point

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
        entries = DialectFeatureEntry.objects.filter(mapitem__group__dialectmap__id=self.kwargs['pk']) \
                                             .filter(feature__dialect__longitude__isnull=False,
                                                     feature__dialect__latitude__isnull=False) \
                                             .values('id', 'entry', 'feature_id',
                                                     dialect_id=F('feature__dialect__id'),
                                                     dialect=F('feature__dialect__name'),
                                                     community=F('feature__dialect__community'),
                                                     longitude=F('feature__dialect__longitude'),
                                                     latitude=F('feature__dialect__latitude'),
                                                     group=F('mapitem__group_id'))

        map_data = [entry_to_map_point(e) for e in entries]

        context = super(DialectMapDetailView, self).get_context_data(**kwargs)
        context.update({
            'map_data_json': json.dumps(map_data, indent=2),
        })
        return context


def entry_to_map_point(entry, focus=False):
    properties = {
        'type':      'entry',
        'group':     entry['group'],
        'entry':     entry['entry'],
        'dialect_id':entry['dialect_id'],
        'dialect':   entry['dialect'],
        'community': entry['community'],
        'url':       reverse('dialects:dialect-feature', args=[entry['id'], entry['feature_id']]),
        'focus':     focus,
    }
    return object_to_map_point(entry, properties=properties)
