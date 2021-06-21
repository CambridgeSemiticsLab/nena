import json
import re
from collections import OrderedDict
from itertools import zip_longest

from django.shortcuts import render
from django.http import JsonResponse, Http404, HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.db.models import Case, When, F, Count
from django.forms import modelform_factory, inlineformset_factory

from dialects.models import Dialect, DialectFeature, DialectFeatureEntry, DialectFeatureExample
from grammar.models import Feature
from gallery.models import Photo
from audio.models import Audio
from dialects.forms import DialectFeatureForm


def homepage(request):
    dialects = Dialect.objects.filter(longitude__isnull=False, latitude__isnull=False) \
                              .values('id', 'name', 'community', 'longitude', 'latitude')

    map_data = [dialect_to_map_point(d) for d in dialects]
    context = {
        'dialects': dialects,
        'hide_toggles': True,
        'map_data_json': json.dumps(map_data, indent=2)
    }
    return render(request, 'index.html', context)

def about(request):
    context = {
    }
    return render(request, 'about.html', context)

def contribute(request):
    context = {
    }
    return render(request, 'contribute.html', context)

def object_to_map_point(object, lon=None, lat=None, properties={}):
    return {
        'id': object['id'],
        'type': 'Feature',
        'geometry': {
            'type': 'Point',
            'coordinates': [lon or object['longitude'], lat or object['latitude']],
        },
        'properties': properties,
    }

def dialect_to_map_point(dialect, focus=False):
    properties = {
        'type':      'dialect',
        'dialect':   dialect['name'],
        'community': dialect['community'],
        'url':       reverse('dialects:dialect-detail', args=[dialect['id']]),
        'focus':     focus,
    }
    return object_to_map_point(dialect, properties=properties)

class DialectListView(ListView):

    name = 'Dialects'
    model = Dialect
    # paginate_by = 20

    def get_queryset(self):
        queryset = Dialect.objects.all()
        if self.request.GET.get('community'):
            queryset = queryset.filter(community=self.request.GET.get('community'))

        if self.request.GET.get('location'):
            queryset = queryset.filter(location=self.request.GET.get('location'))

        return queryset

    def get_context_data(self, **kwargs):
        context = super(DialectListView, self).get_context_data(**kwargs)
        context.update({
            'communities':      Dialect.COMMUNITIES,
            'chosen_community': self.request.GET.get('community'),
            'locations':        Dialect.LOCATIONS,
            'chosen_location':  self.request.GET.get('location'),
        })
        return context

class DialectDetailView(DetailView):

    name = 'Dialect details'
    model = Dialect

    def get_context_data(self, **kwargs):
        dialects = Dialect.objects.filter(longitude__isnull=False, latitude__isnull=False) \
                                  .values('id', 'name', 'community', 'longitude', 'latitude')
        map_data = [dialect_to_map_point(d, (d['id']==self.object.id)) for d in dialects]

        context = super(DialectDetailView, self).get_context_data(**kwargs)
        context.update({
            'photos': Photo.objects.filter(dialect=self.object)[0:5],
            'audio':  Audio.objects.filter(dialect=self.object) \
                           .order_by(
                                F('translation').desc(nulls_last=True),
                                F('transcript').desc(nulls_last=True)
                           )[0:5],
            'feature_count': DialectFeature.objects.filter(dialect=self.object).count(),
            'map_data_json': json.dumps(map_data, indent=2),
            'map_center': [self.object.latitude, self.object.longitude]
        })
        return context

class DialectCreateView(CreateView):
    model = Dialect
    fields = ['name', 'code', 'community', 'country', 'location', 'latitude', 'longitude', 'source', 'information', 'remarks']

    def get_context_data(self, **kwargs):
        dialects = Dialect.objects.values_list('id', 'name')
        context = super(DialectCreateView, self).get_context_data(**kwargs)
        context.update({'dialects': dialects})
        return context

    def form_valid(self, form):
        response = super(DialectCreateView, self).form_valid(form)
        new_dialect     = self.object

        # if a base dialect is selected, clone all of its features and entries into this new one
        base_dialect_id = int(self.request.POST.get('base_dialect_id'))
        if base_dialect_id:
            base_dialect = Dialect.objects.filter(id=base_dialect_id).first()
            for feature in base_dialect.features.all():
                entries = feature.entries.all()

                feature.pk = None
                feature.dialect = new_dialect
                feature.save()

                for entry in entries:
                    entry.pk = None
                    entry.feature = feature
                    entry.save()

        return response

class DialectUpdateView(UpdateView):
    model = Dialect
    fields = ['name', 'code', 'community', 'country', 'location', 'latitude', 'longitude', 'source', 'information', 'remarks']
#    template_name_suffix = '_update_form'

class DialectDeleteView(DeleteView):
    model = Dialect
    success_url = reverse_lazy('dialects:dialect-list')

def get_section_root(section):
    if section:
        # Make trailing dots consistent and workaround "x.0" inconsistency
        section = section.rstrip('.')
        section = section if section[-1] == '0' else section + '.'

    root = Feature.objects.filter(fullheading=section).first()
    if section and not root:
        raise Http404('No sections match \'{}\''.format(section))
    return root


def make_breadcrumb_bits(feature):
    """ takes a feature and returns a breakdown of its parents features suitable for turning
        into a breadcrumb trail; a list of tuples like ('fullheading', 'number to link on')
        eg. 3.2.1 turns into (('3.0', '3'), ('3.2', '2'), ('3.2.1', '1'))
    """
    if feature:
        heading_numbers = feature.fullheading.split('.')[0:-1]
        breadcrumb_bits = (('.'.join(heading_numbers[0:i+1]), x + '.') for i, x in enumerate(heading_numbers))
        breadcrumb_bits = ((x[0]+('.0' if i == 0 else ''), x[1]) for i, x in enumerate(breadcrumb_bits))
    else:
        breadcrumb_bits = []

    return breadcrumb_bits


@login_required
def setup_comparison(request, dialect_id_string):
    ''' add or remove dialects from the features tree
    '''
    dialect_ids = [int(x) for x in dialect_id_string.split(',')]

    # Clean the request url by adding or removing dialects
    compare_id = request.GET.get('compare_with')
    remove_id  = request.GET.get('remove_compare')
    if compare_id or remove_id:
        if compare_id:
            dialect_ids.append(int(compare_id))
        if remove_id:
            dialect_ids.remove(int(remove_id))
        id_string = ','.join([str(x) for x in dialect_ids])
        view_name = 'dialects:dialect-grammar'
        args = [id_string]
        if request.GET.get('section'):
            view_name = 'dialects:dialect-grammar-section'
            args.append(request.GET.get('section'))
        return HttpResponseRedirect(reverse(view_name, args=args))


@login_required
def features_of_dialect(request, dialect_id_string, section=None):
    '''The grammar features of a chosen dialect, in tree format '''
    dialect_ids = [int(x) for x in dialect_id_string.split(',')]

    is_bulk_edit = request.GET.get('edit') or False
    base_dialect_id = int(request.GET.get('base_on', 0))
    if is_bulk_edit and base_dialect_id:
        dialect_ids.append(base_dialect_id)

    preserved    = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(dialect_ids)])
    dialects     = Dialect.objects.filter(id__in=dialect_ids).order_by(preserved)
    chosen_root  = get_section_root(section)

    # annotated lists are an efficient way of getting a big chunk of a treebeard tree
    # see: https://django-treebeard.readthedocs.io/en/latest/api.html#treebeard.models.Node.get_annotated_list
    max_depth    = None
    feature_list = Feature.get_annotated_list(parent=chosen_root, max_depth=max_depth)

    # process bulk save if that's what's happening
    # todo - separate this out into a different function, with own url and pass feature id list
    #        through form so it doesn't rely on the above code
    bulk_text   = request.POST.get('bulk_edit', None)
    entry_regex = r'^\s*(?P<entry>.+?)\s*(?P<frequency>\b[MPmp]\b){0,1}\s*(?P<comment>\".+\")?\s*$'
    if bulk_text is not None:
        row_texts = bulk_text.split('\n')
        for row_text, feature in zip_longest(row_texts, feature_list[1:], fillvalue=''):  # skip first feature as it matches the top-level group
            dfes = []
            for entry_text in row_text.split('~'):
                matches = re.match(entry_regex, entry_text.strip('\r').strip(' '))
                if not matches:
                    continue
                matches_dict = matches.groupdict()
                if len(matches_dict['entry'].strip(' ')) < 1:
                    continue
                matches_dict['frequency'] = matches_dict['frequency'].upper() if matches_dict['frequency'] else 'P'
                matches_dict['comment']   = matches_dict['comment'].strip('"') if matches_dict['comment'] else None
                dfes.append(DialectFeatureEntry(**matches_dict))

            # load the existing DialectFeature or prepare a new one
            df = DialectFeature.objects.filter(dialect=dialects[0].id, feature=feature[0].id).first()
            if not df:
                df = DialectFeature(dialect_id=dialects[0].id, feature_id=feature[0].id)
                df.save()

            df.entries.all().delete()  # clear any existing entries
            df.entries.set(dfes, bulk=False)

            if len(dfes) < 1:  # delete the Dialect Feature if no entries were submitted
                df.delete()

        return HttpResponseRedirect(reverse('dialects:dialect-grammar-section', args=(dialects[0].id, section)))


    # ( feature, stuff, [{df: _, entries: [], examples: []}, {df: _, entries: [], examples: []}, ...] )

    base_path = chosen_root.path if chosen_root else ''
    preserved = Case(*[When(dialect_id=pk, then=pos) for pos, pk in enumerate(dialect_ids)])
    dialectfeatures = DialectFeature.objects.filter(dialect__in=dialect_ids) \
                                            .filter(feature__path__startswith=base_path) \
                                            .values('id', 'dialect_id', 'feature_id', 'feature__path', 'feature__fullheading',
                                                    'is_absent', 'introduction', 'comment', 'category') \
                                            .order_by('feature__path', preserved)

    entries = DialectFeatureEntry.objects.filter(feature__dialect__in=dialect_ids) \
                                           .filter(feature__feature__path__startswith=base_path) \
                                           .values('feature__id', 'id', 'entry', 'frequency', 'comment') \
                                           .order_by('feature__feature__path', '-frequency')

    entries_dict = {}
    for x in entries:
        entries_dict.setdefault(x['feature__id'], []).append(x)


    examples_dict = {}
    if is_bulk_edit:
        entries = entries.filter(feature__feature__depth=max_depth)
    elif len(dialects) == 1:
        examples = DialectFeatureExample.objects.filter(feature__dialect__in=dialect_ids) \
                                                .filter(feature__feature__path__startswith=base_path) \
                                                .values('feature__id', 'id', 'example') \
                                                .order_by('feature__feature__path')
        for x in examples:
            examples_dict.setdefault(x['feature__id'], []).append(x)


    num_features = 0
    dialectfeatures_dict = {}
    for x in dialectfeatures:
        num_features += 1
        x.update({
            'entries': entries_dict.get(x['id'], []),
            'examples': examples_dict.get(x['id'], []),
        })
        dialectfeatures_dict.setdefault(x['feature_id'], []).append(x)

    for i, feature in enumerate(feature_list):
        feature_list[i] = (feature[0], feature[1], dialectfeatures_dict.get(feature[0].id, []))


    context = {
        'dialect_ids':  dialect_ids,
        'dialects':     dialects,
        'section':      chosen_root,
        'breadcrumb_bits': make_breadcrumb_bits(chosen_root),
        'feature_list': feature_list,
        'num_features': num_features,
        'all_dialects': Dialect.objects.all() \
                                       .filter(features__feature__path__startswith=base_path) \
                                       .exclude(id__in=dialect_ids) \
                                       .annotate(feature_count=Count('features'))
                                       .values_list('id', 'name', 'feature_count'),
        'bulk_edit':    is_bulk_edit,
    }


    if context['bulk_edit']:
        def encode_entry(entry):
            encoded_entry = entry['entry']
            if entry['frequency'] not in ('P', None):
                encoded_entry += ' {}'.format(entry['frequency'])
            if entry['comment']:
                encoded_entry += ' "{}"'.format(entry['comment'])
            return encoded_entry

        raw_rows = []
        for feature, info, dialectfeatures in feature_list[1:]:
            if not dialectfeatures:
                raw_rows.append('')
                continue

            dialect_idx = -1 if base_dialect_id else 0
            entries     = dialectfeatures[dialect_idx].get('entries', [])
            raw_rows.append(' ~ '.join([encode_entry(x) for x in entries]))

        # join using html newline entity to prevent textarea ignoring first newline char
        # see: https://stackoverflow.com/a/49604548
        raw_text = '&#13;'.join(raw_rows)
        context.update({
            'raw_text': raw_text,
        })
    if chosen_root:
        context['total_features'] = DialectFeature.objects.filter(dialect__in=dialect_ids).count()

    return render(request, 'grammar/feature_list.html', context)


class DialectFeatureDetailView(DetailView):

    name = 'DialectFeatureDetail'
    model = DialectFeature

    def get_context_data(self, **kwargs):
        context = super(DialectFeatureDetailView, self).get_context_data(**kwargs)
        context.update({
            'entries': DialectFeatureEntry.objects.filter(feature=context['object'].id),
            'examples': DialectFeatureExample.objects.filter(feature=context['object'].id),
        })
        return context


def dialect_feature_pane(request, dialect_id, feature_heading):
    """ renders just a snippet of html that contains details of the DialectFeature, for ajaxing
    """
    df_dict = DialectFeature.objects.filter(dialect=dialect_id, feature__fullheading=feature_heading) \
                                    .values('id', 'dialect_id', 'feature__fullheading', 'is_absent', 'introduction', 'comment') \
                                    .first()
    context = {
        'dialect_id':      dialect_id,
        'feature_heading': feature_heading,
    }
    if df_dict:
        df_dict['entries'] = DialectFeatureEntry.objects.filter(feature_id=df_dict['id']) \
                                                        .values('entry', 'comment')
        context.update({
            'df': df_dict,
        })
    return render(request, 'dialects/_dialectfeature_pane.html', context)


@staff_member_required
def dialect_feature_edit(request, dialect_id, feature_heading):
    """ edit page for DialectFeature details as well as adding, changing and removing its examples
    """
    feature = Feature.objects.get(fullheading=feature_heading)
    dialect = Dialect.objects.get(id=dialect_id)
    df      = DialectFeature.objects.filter(dialect=dialect_id,
                                            feature__fullheading=feature_heading) \
                                    .first()

    if request.POST.get('delete'):
        if df:
            df.delete()
        return HttpResponseRedirect(reverse('dialects:dialect-detail', args=(dialect_id,)))

    if not df:
        df = DialectFeature(dialect=dialect, feature=feature)

    shared_kwargs = {
        'initial': [{'frequency': 'M' if df and df.entries.count() > 0 else 'P'}],
        'instance': df,
    }
    dfe_formset_class = inlineformset_factory(DialectFeature, DialectFeatureEntry,
                                              fields=('entry', 'frequency', 'comment'), extra=1)

    postvars    = request.POST or None
    df_form     = DialectFeatureForm(postvars, instance=df)
    dfe_formset = dfe_formset_class(postvars, **shared_kwargs)

    if request.method == 'POST' and dfe_formset.is_valid():
        df_form.save()
        dfe_formset.save()
        return HttpResponseRedirect(reverse('dialects:dialect-feature', args=(dialect.id, df.id)))

    context = {
        'dialect':     dialect,
        'feature':     feature,
        'df':          df,
        'df_form':     df_form,
        'dfe_formset': dfe_formset,
    }
    return render(request, 'dialects/dialectfeature_edit.html', context)


def build_dialects_json(request):
    dialects = Dialect.objects.filter(code__isnull=False).values('name', 'code', 'location')

    return JsonResponse([{'code': d['code'],
                          'name': d['name'],
                          'location': dict(Dialect.LOCATIONS).get(d['location'],''),
                          'source': 'Fieldwork by Geoffrey Khan',
                         } for d in dialects], safe=False, json_dumps_params={'indent': 2, 'ensure_ascii': False})


def problems(request):
    """ a staff-only page detailing data issues that we think we can fix automatically, and some we can't
    """
    context = {}

    types = [
        ('simple_span',      '^\<span class=aramaic\>.*?\<\/span\>$'),
        ('span_suffix',      '^\<span class=aramaic\>.*?\<\/span\>[^\<]+$'),
        ('span_prefix',      '^[^\<]+\<span class=aramaic\>.*?\<\/span\>$'),
        ('span_prepost',     '^[^\<]+\<span class=aramaic\>.*?\<\/span\>[^\<]+$'),
        ('span_exemplified', '^Exemplified by (the verb )?<span class=aramaic\>.*?\<\/span\>[^\<]*?$'),
        ('span_cropl',       '^ *span class=aramaic\>.*?\<\/span\> *$'),
        ('span_extral',      '^\>\<span class=aramaic\>.*?\<\/span$'),
        ('span_cropr',       '^ *\<span class=aramaic\>.*?\<\/span[^\>]*$'),
        ('span_span',        '^ *\<span class=aramaic\>.*?\<span\> *$'),
        ('spana_spana',      '^\<span class=aramaic\>.*?\<span class=aramaic\>$'),
        ('any_span',         '^.*?span.*?$'),
        ('span_incomplete',  '^\<span class=aramaic\>[^\<]+$'),
        ('double_span',      '^\<span class=aramaic\>.*?\<\/span\> ~ \<span class=aramaic\>.*?\<\/span\>$'),
        ('triple_span',      '^\<span class=aramaic\>.*?\<\/span\> ~ \<span class=aramaic\>.*?\<\/span\> ~ \<span class=aramaic\>.*?\<\/span\>$'),
        ('quad_span',        '^\<span class=aramaic\>.*?\<\/span\> ~ \<span class=aramaic\>.*?\<\/span\> ~ \<span class=aramaic\>.*?\<\/span\> ~ \<span class=aramaic\>.*?\<\/span\>$'),
        ('sup_x',            '\<sup\>\+\<\/sup\>'),
        ('sup_y',            '\<sup\>\y\<\/sup\>'),
        ('yes',              '^ *Yes *$'),
        ('yes_see_eg',       '^ *Yes \(see examples\) *$'),
        ('yes_loanwords',    '^ *Yes \(mostly loanwords\) *$'),
        ('yes_eg',           '^ *Yes \(\<span class=aramaic\>.*?\<\/span\> *\)*$'),
        ('no',               '^ *No *$'),
        ('no_past_base',     '^ *No, general past base only *$'),
        ('no_stative',       '^ *No: General stative participle only *$'),
        ('no_loanwords',     '^ *No, restricted to loanwords *$'),
        ('loanwords',        'loan'),
        ('not_present',      '^ *XXX *$'),
        ('blank',            '^ *$'),
        ('unsure',           '^\?*$'),
        ('none',             '^ *None *$'),
        ('none_attested',    '^ *None attested\.? *$'),
        ('dash',             '^ *- *$'),
        ('test',             '^ *test *$'),
        ('as_usual',         '^ *As usual *$'),
        ('penultiamte',      '^ *Penultimate *$'),
        ('assimilation',     '^ *Regular assimilation of L-suffix and resulting gemination of \/[rn]\/\. *$'),
    ]
    os = DialectFeatureEntry.objects
    canfix = [
        (type,
         os.filter(entry__iregex=regex).count(),
         os.filter(entry__iregex=regex) \
           .values_list('entry', 'feature__dialect_id', 'feature_id')[0:30]
        ) for type, regex in types
    ]

    # Temporarily removed
    # cantfix = DialectFeatureEntry.objects
    # for type, regex in types:
        # cantfix = cantfix.exclude(entry__iregex=regex)
    # cantfix = cantfix.values_list('entry', 'feature__dialect_id', 'feature_id')
    context = {
        'canfix': canfix,
        # 'cantfix': cantfix[0:1000],
        # 'cantfix_count': cantfix.count(),
    }
    return render(request, 'dialects/problems.html', context)
