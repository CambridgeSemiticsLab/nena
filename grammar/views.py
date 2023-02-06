import csv
import json
from collections import defaultdict, Counter

from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.db.models import Prefetch, Count, F, Q
from django.urls import reverse
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
    ''' list all dialects with corresponding entries for a given feature '''
    feature = Feature.objects.get(pk=pk)
    is_absent = request.GET.get('is_absent', 'False')=='true'
    prefetch_entries = Prefetch('entries', DialectFeatureEntry.objects.order_by('-frequency'))
    queryset = DialectFeature.objects.filter(feature_id=feature.id, is_absent=is_absent,
                                             dialect__group=request.session['dialect_group_id']) \
                             .select_related('dialect') \
                             .prefetch_related(prefetch_entries) \
                             .order_by('dialect__name')
    unfiltered_count = queryset.count()

    if request.method == "POST" and request.GET.get('mark_without'):
        dialect_ids = list(int(x) for x in request.POST.getlist('checked_dialect_id'))
        if DialectFeature.objects.filter(dialect_id__in=dialect_ids, feature=feature).count():
            msg = 'Error: at least one of the submitted dialects already has an entry for this feature'
            messages.add_message(request, messages.INFO, msg)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        for dialect in Dialect.objects.filter(id__in=dialect_ids):
            df = DialectFeature(dialect=dialect, feature=feature, is_absent=True)
            df.save()
        msg = '{} dialects marked as not having this feature'.format(len(dialect_ids))
        messages.add_message(request, messages.INFO, msg)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

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

    all_dialects_qs = Dialect.objects.filter(group_id=request.session['dialect_group_id'])

    unknown_dialect_ids = all_dialects_qs.exclude(features__feature=feature).values_list('id', flat=True)
    is_unknown = request.GET.get('is_unknown', 'False')=='true'
    if is_unknown:
        queryset = list(DialectFeature(dialect=dialect, feature=feature)
                        for dialect in all_dialects_qs.filter(id__in=unknown_dialect_ids))

    num_dialects = all_dialects_qs.count()
    num_unknown  = len(unknown_dialect_ids)
    num_with     = unfiltered_count
    num_without  = num_dialects - num_unknown - unfiltered_count
    if is_absent:
        num_with, num_without = num_without, num_with

    frequency_summary = defaultdict(int)
    for dialect_feature in queryset:
        for entry in dialect_feature.entries.all():
            frequency_summary[entry.entry] += 1
    frequency_summary = sorted(frequency_summary.items(), key=lambda x: x[1], reverse=True)

    group_string = request.GET.get('groups', '')
    group_map = decode_group_map(group_string)
    group_summary = dict(Counter(group_map.values()))
    dialect_features = []
    for dialect_feature in queryset:
        dialect_feature.group_key = group_map.get(dialect_feature.dialect_id, None)
        dialect_features.append(dialect_feature)

    context = {
        'with_without_unknown': 'unknown' if is_unknown else 'without' if is_absent else 'with',
        'feature':          feature,
        'dialect_features': dialect_features,
        'frequency_summary': frequency_summary,
        'group_summary':    group_summary,
        'num_dialects':     num_dialects,
        'num_with':         num_with,
        'num_without':      num_without,
        'num_unknown':      num_unknown,
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

    if request.GET.get("as_csv"):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="Dialects with {feature.fullheading} {feature.name}.csv"'
        import codecs
        response.write(codecs.BOM_UTF8)
        writer = csv.writer(response)
        writer.writerow(("Dialect", "Entry", "Frequency", "Community", "Location", "Country", "Latitude", "Longitude"))
        for feature in dialect_features:
            dialect = feature.dialect
            for entry in feature.entries.all():
                writer.writerow((dialect.name, entry.entry, entry.frequency, dialect.community, dialect.location, dialect.country, dialect.latitude, dialect.longitude))
        return response

    return render(request, 'grammar/feature_detail.html', context)


@login_required
def map_of_feature(request, pk):
    '''  '''
    if request.method == "POST":
        group_keys = request.POST.getlist('group_key')
        dialect_ids   = request.POST.getlist('dialect_id')
        groups_dict = defaultdict(list)
        for id, key in zip(dialect_ids, group_keys):
            if key == '0': continue
            groups_dict[key].append(id)

        url = reverse("grammar:feature-map", kwargs={'pk':pk})
        querystring = MAP_GROUP_DELIMITER.join(f"{k}{MAP_GROUP_EQUALS}{','.join(ids)}" for k, ids in groups_dict.items())
        url = (url + "?groups=" + querystring) if groups_dict else url
        return HttpResponseRedirect(url)

    from dialectmaps.views import entry_to_map_point
    entries = DialectFeatureEntry.objects \
        .filter(
            feature__feature_id=pk,
            feature__dialect__group=request.session['dialect_group_id'],
            feature__dialect__longitude__isnull=False,
            feature__dialect__latitude__isnull=False) \
        .values(
            'id', 'entry', 'feature_id',
            dialect_id=F('feature__dialect__id'),
            dialect=F('feature__dialect__name'),
            community=F('feature__dialect__community'),
            longitude=F('feature__dialect__longitude'),
            latitude=F('feature__dialect__latitude'),
            group=F('entry'))


    group_string = request.GET.get('groups', '')
    group_map = decode_group_map(group_string)

    if group_map:
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
        'group_string':     group_string,
    }

    if request.GET.get('community'):
        context.update({'chosen_community_name': dict(Dialect.COMMUNITIES)[request.GET.get('community')]})

    if request.GET.get('location'):
        context.update({'chosen_location_name': dict(Dialect.LOCATIONS)[request.GET.get('location')]})

    return render(request, 'dialectmaps/dialectmap_detail.html', context)


MAP_GROUP_DELIMITER = "-/-"
MAP_GROUP_EQUALS = ":"

def decode_group_map(group_string):
    """ return a dict of id -> group key from the given string """
    group_map = {}
    for group in group_string.split(MAP_GROUP_DELIMITER):
        if group == "": continue
        key, ids = group.split(MAP_GROUP_EQUALS)
        for id in ids.split(","):
            group_map[int(id)] = key
    return group_map


@login_required
def coverage_check(request, type="grammar"):
    ''' returns a csv summary of which grammar features have what level of completeness '''
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{}_coverage.csv"'.format(type)

    if type == "grammar":
        headings = {
            'id'          : 'Feature ID',
            'fullheading' : 'Section Number',
            'name'        : 'Section Name',
            'num_dialects': 'Dialects Populated',
        }
        results = Feature.objects.filter() \
                         .annotate(num_dialects=Count('dialectfeature', distinct=True)) \
                         .values_list(*headings.keys())
    elif type == "dialects":
        headings = {
            'id'          : 'Dialect ID',
            'name'        : 'Name',
            'location'    : 'Location',
            'longitude'   : 'Longitude',
            'latitude'    : 'Latitude',
            'num_features': 'Num Features',
        }
        query = Dialect.objects.filter(group_id=request.session['dialect_group_id']) \
                               .annotate(num_features=Count('features', distinct=True)) \

        sections = {}
        for i in range(1, 18):
            sections['section_{}'.format(i)] = 'Section {}.0'.format(i)
            arg = {'section_{}'.format(i): Count('features', distinct=True, filter=Q(features__feature__fullheading__startswith="{}.".format(i)))}
            query = query.annotate(**arg)

        headings.update(sections)

        results = query.order_by('name').values_list(*headings.keys())

    writer = csv.writer(response)
    writer.writerow(headings.values())
    for row in results:
        writer.writerow(row)

    return response
