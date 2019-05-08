import json

from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse, HttpResponse
from django.db.models import Prefetch, Count, F
from django.urls import reverse_lazy
from django.shortcuts import render

from grammar.models import Feature
from dialects.models import Dialect, DialectFeature, DialectFeatureEntry, DialectFeatureExample
from dialects.views import get_section_root

@staff_member_required
def features(request, section=None):
    '''The grammar feature list page with the main categories.'''
    chosen_root = get_section_root(section)

    base_path      = chosen_root.path if chosen_root else ''
    dialect_counts = Feature.objects.filter(path__startswith=base_path) \
                                    .annotate(num_dialects=Count('dialectfeature__id')) \
                                    .values_list('num_dialects') \
                                    .order_by('path')

    # force list conversion else dialect_counts[i] lookup below is *slow*
    dialect_counts = list(dialect_counts)

    feature_list = Feature.get_annotated_list(parent=chosen_root)

    for i in range(0, len(feature_list)):
        feature_list[i][1]['dialect_count'] = dialect_counts[i][0]

    context = {
        'section': chosen_root,
        'feature_list': feature_list,
        'dialect_counts': dialect_counts,
    }
    return render(request, 'grammar/feature_list.html', context)


@staff_member_required
def dialects_with_feature(request, pk):
    ''' Faster way to list all dialects with corresponding entries for a given feature '''
    ''' todo - replace FeatureDetailView and FeatureParadigmView with this or similar '''
    feature = Feature.objects.get(pk=pk)
    prefetch_entries = Prefetch('entries', DialectFeatureEntry.objects.order_by('-frequency'))
    queryset = DialectFeature.objects.filter(feature_id=feature.id) \
                             .select_related('dialect') \
                             .prefetch_related(prefetch_entries) \
                             .order_by('dialect__name')

    # todo: combine this filtering logic with similar in dialects.DialectListView
    if request.GET.get('community'):
        queryset = queryset.filter(dialect__community=request.GET.get('community'))

    if request.GET.get('location'):
        queryset = queryset.filter(dialect__location=request.GET.get('location'))

    if request.GET.get('entry'):
        queryset = queryset.filter(entries__entry=request.GET.get('entry'))

    context = {
        'feature': feature,
        'dialect_features': queryset,
        'communities':      Dialect.COMMUNITIES,
        'chosen_community': request.GET.get('community'),
        'locations':        Dialect.LOCATIONS,
        'chosen_location':  request.GET.get('location'),
        'entry_filter':     request.GET.get('entry', None),
    }
    return render(request, 'grammar/feature_detail.html', context)


@staff_member_required
def map_of_feature(request, pk):
    '''  '''
    from dialectmaps.views import entry_to_map_point
    entries = DialectFeatureEntry.objects.filter(feature__feature_id=pk) \
                                         .filter(feature__dialect__longitude__isnull=False,
                                                 feature__dialect__latitude__isnull=False) \
                                         .values('id', 'entry', 'feature_id',
                                                 dialect=F('feature__dialect__name'),
                                                 community=F('feature__dialect__community'),
                                                 longitude=F('feature__dialect__longitude'),
                                                 latitude=F('feature__dialect__latitude'),
                                                 group=F('entry'))

    feature = Feature.objects.get(pk=pk)
    map_data = [entry_to_map_point(e) for e in entries]
    context = {
        'feature': feature,
        'map_data_json': json.dumps(map_data, indent=2),
        'view': {'name': feature}
    }

    return render(request, 'dialectmaps/dialectmap_detail.html', context)


class FeatureParadigmView(DetailView):
    '''Details for group of features across all dialects that form a language paradigm'''

    model = Feature
    template_name = 'grammar/paradigm_detail.html'

    def get_context_data(self, **kwargs):

        context = super(FeatureParadigmView, self).get_context_data(**kwargs)
        dialects = {}
        gf = Feature.objects.filter(pk=self.kwargs['pk']).first() # the grammar feature
        paradigm = [gf] + list(gf.get_children()) # list of all the paradigm features for the grammar feature
        for df in DialectFeature.objects.filter(feature=self.kwargs['pk']).order_by('dialect'):
            d = df.dialect
            for p in paradigm:
                features = DialectFeature.objects.filter(feature=p, dialect=d)
                for f in features:
                    mappable = True if (f.dialect.latitude and f.dialect.longitude) else False
                    entries = {}
                    for e in f.entries.all():
                        if e.feature.dialect.pk not in dialects:
                            dialects[e.feature.dialect.pk] = {}
                        if e.frequency == 'P':
                            entries['primary'] = e.entry
                        elif e.frequency == 'M':
                            if 'marginal' in entries:
                                entries['marginal'].append(e.entry)
                            else:
                                entries['marginal'] = [e.entry]
                        dialects[e.feature.dialect.pk] = {'name': e.feature.dialect.name, 'mappable': mappable, 'entries': entries }
        context['dialects'] = dialects
        return context

class FeatureListJSONView(ListView):

    model = Feature

    def get_context_data(self, **kwargs):
        context = super(FeatureListJSONView, self).get_context_data(**kwargs)
        return context

    def render_to_response(self, context):
        def unwrap(lst, res):
            '''Transform treebeard's dump_bulk() into something jstree can use'''
            initial = [1, 41, 2236, 2289]
            for i in lst:
                res.append({'id':i['id'], 'text':i['data']['fullheading']+'&nbsp;'+i['data']['name'], 'a_attr':{'href':reverse_lazy('grammar:feature-detail', args=[str(i['id'])])}})
                if 'children' in i.keys():
                    if i['data']['group']:
                        res[-1]['type'] = 'paradigm'
                        res[-1]['a_attr'] = {'href':reverse_lazy('grammar:feature-paradigm', args=[str(i['id'])])}
                    else:
                        res[-1]['type'] = 'branch'
                    res[-1]['children'] = []
                    unwrap(i['children'], res[-1]['children'])
                else:
                    res[-1]['type'] = 'leaf'
                if i['id'] in initial:
                    res[-1]['state'] = {'opened': 'true'}
                    res[-1]['type'] = 'root' # this overwrites branch from above

        result = []
        data = Feature.dump_bulk()
        unwrap(data, result)
        return JsonResponse(result, safe=False)

class FeatureDetailJSONView(DetailView):
    '''Details for a specific grammar feature across all dialects'''

    model = Feature

    def get_context_data(self, **kwargs):
        context = super(FeatureDetailView, self).get_context_data(**kwargs)
        dialects = {}
        features = DialectFeature.objects.filter(feature=self.kwargs['pk']).order_by('dialect')
        for f in features:
            mappable = True if (f.dialect.latitude and f.dialect.longitude) else False
            entries = {}
            for e in f.entries.all():
                if e.feature.dialect.pk not in dialects:
                    dialects[e.feature.dialect.pk] = {}
                if e.frequency == 'P':
                    entries['primary'] = e.entry
                elif e.frequency == 'M':
                    if 'marginal' in entries:
                        entries['marginal'].append(e.entry)
                    else:
                        entries['marginal'] = [e.entry]
                dialects[e.feature.dialect.pk] = {'name': e.feature.dialect.name, 'mappable': mappable, 'entries': entries }
        context['dialects'] = dialects
        return context

    def render_to_response(self, context):
        pass
