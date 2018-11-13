from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.db.models import Q
from django.urls import reverse_lazy

from grammar.models import Feature
from dialects.models import Dialect, DialectFeature, DialectFeatureEntry, DialectFeatureExample

class FeatureListView(ListView):
    '''The grammar feature list page with the main categories.'''
    model = Feature
    name = "Grammatical description"

    context_object_name = 'feature_list'

    def get_context_data(self, **kwargs):
        context = super(FeatureListView, self).get_context_data(**kwargs)
        context['annotated_list'] = Feature.get_annotated_list(max_depth=2)
        return context


class FeatureDetailView(DetailView):
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

class FeatureParadigmView(DetailView):
    '''Details for group of features across all dialects that form a language paradigm'''

    model = Feature

    def get_context_data(self, **kwargs):
        context = super(FeatureParadigmView, self).get_context_data(**kwargs)
        dialects = {}
        gf = DialectFeature.objects.filter(feature=self.kwargs['pk']).first().feature # the grammar feature
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
