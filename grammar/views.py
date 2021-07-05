import json

from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.db.models import Prefetch, Count, F
from django.urls import reverse_lazy
from django.shortcuts import render

from grammar.models import Feature
from dialects.models import Dialect, DialectFeature, DialectFeatureEntry, DialectFeatureExample
from dialects.views import get_section_root, make_breadcrumb_bits

@login_required
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
        feature_list[i] = (*feature_list[i], [])



    context = {
        'section': chosen_root,
        'breadcrumb_bits': make_breadcrumb_bits(chosen_root),
        'feature_list': feature_list,
        'dialect_counts': dialect_counts,
    }
    return render(request, 'grammar/feature_list.html', context)


@login_required
def dialects_with_feature(request, pk):
    ''' Faster way to list all dialects with corresponding entries for a given feature '''
    ''' todo - replace FeatureDetailView and FeatureParadigmView with this or similar '''
    feature = Feature.objects.get(pk=pk)
    prefetch_entries = Prefetch('entries', DialectFeatureEntry.objects.order_by('-frequency'))
    queryset = DialectFeature.objects.filter(feature_id=feature.id) \
                             .select_related('dialect') \
                             .prefetch_related(prefetch_entries) \
                             .order_by('dialect__name')

    search_term = request.POST.get('find', '')
    replacement = request.POST.get('replace', '')
    if request.method == "POST":
        df_ids = queryset.values_list('id', flat=True)
        matching_entries = DialectFeatureEntry.objects.filter(entry=search_term, feature_id__in=df_ids)

        if not matching_entries.count():
            msg = 'No entries match "{}"'.format(search_term)
            messages.add_message(request, messages.INFO, msg)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        if request.POST.get('confirm'):
            for entry in matching_entries:
                entry.entry = replacement
                entry.save()
            msg = 'Updated {} entries from "{}" to "{}"'.format(matching_entries.count(), search_term, replacement)
            messages.add_message(request, messages.INFO, msg)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        queryset = queryset.filter(entries__entry=request.POST['find'])

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
        'search_term':      search_term,
        'replacement':      replacement,
    }

    if request.GET.get('community'):
        context.update({'chosen_community_name': dict(Dialect.COMMUNITIES)[request.GET.get('community')]})

    if request.GET.get('location'):
        context.update({'chosen_location_name': dict(Dialect.LOCATIONS)[request.GET.get('location')]})

    return render(request, 'grammar/feature_detail.html', context)


@login_required
def map_of_feature(request, pk):
    '''  '''
    from dialectmaps.views import entry_to_map_point
    entries = DialectFeatureEntry.objects.filter(feature__feature_id=pk) \
                                         .filter(feature__dialect__longitude__isnull=False,
                                                 feature__dialect__latitude__isnull=False) \
                                         .values('id', 'entry', 'feature_id',
                                                 dialect_id=F('feature__dialect__id'),
                                                 dialect=F('feature__dialect__name'),
                                                 community=F('feature__dialect__community'),
                                                 longitude=F('feature__dialect__longitude'),
                                                 latitude=F('feature__dialect__latitude'),
                                                 group=F('entry'))

    group_map = None
    if request.POST:
        group_numbers = request.POST.getlist('group_number')
        dialect_ids   = request.POST.getlist('dialect_id')
        group_map = {int(x):y for x, y in zip(dialect_ids, group_numbers) if y != '0'}
        entries = entries.filter(feature__dialect__id__in=group_map.keys())

    # todo: combine this filtering logic with similar in dialects.DialectListView
    if request.GET.get('community'):
        entries = entries.filter(feature__dialect__community=request.GET.get('community'))

    if request.GET.get('location'):
        entries = entries.filter(feature__dialect__location=request.GET.get('location'))

    if request.GET.get('entry'):
        entries = entries.filter(entry=request.GET.get('entry'))

    feature = Feature.objects.get(pk=pk)
    map_data = [entry_to_map_point(e) for e in entries]

    if group_map:
        for i, _ in enumerate(map_data):
            map_data[i]['properties']['group'] = group_map[map_data[i]['properties']['dialect_id']]

    context = {
        'feature': feature,
        'map_data_json': json.dumps(map_data, indent=2),
        'view': {'name': feature},
        'communities':      Dialect.COMMUNITIES,
        'chosen_community': request.GET.get('community'),
        'locations':        Dialect.LOCATIONS,
        'chosen_location':  request.GET.get('location'),
        'entry_filter':     request.GET.get('entry'),
    }

    if request.GET.get('community'):
        context.update({'chosen_community_name': dict(Dialect.COMMUNITIES)[request.GET.get('community')]})

    if request.GET.get('location'):
        context.update({'chosen_location_name': dict(Dialect.LOCATIONS)[request.GET.get('location')]})

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
