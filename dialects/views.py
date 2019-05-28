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

from dialects.models import Dialect, DialectFeature, DialectFeatureEntry
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
        'hide_color_toggle': True,
        'map_data_json': json.dumps(map_data, indent=2)
    }
    return render(request, 'index.html', context)

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
                data['features'].append({
                    "id": d.pk,
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [d.longitude, d.latitude]},
                        "properties": {
                            "name": d.name,
                            "community": d.community,
                            "url": d.get_absolute_url(),
                        }
                    })
        return JsonResponse(data, safe=False)

class DialectDetailJSONView(DetailView):
    name = 'Dialects'
    model = Dialect

    def get_context_data(self, **kwargs):
        context = super(DialectDetailJSONView, self).get_context_data(**kwargs)
        return context

    def render_to_response(self, context):
        for d in [context['dialect']]:
            data = {"id": d.pk, "type": "Feature", "geometry": {"type": "Point", "coordinates": [d.longitude, d.latitude]}, "properties": {"name": d.name, "community": d.community, "url": d.get_absolute_url(), 'focus': True}}
            return JsonResponse(data, safe=False)

class DialectCreateView(CreateView):
    model = Dialect
    fields = ['name', 'community', 'country', 'location', 'latitude', 'longitude', 'source', 'information', 'remarks']

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
    fields = ['name', 'community', 'country', 'location', 'latitude', 'longitude', 'source', 'information', 'remarks']
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


@login_required
def features_of_dialect(request, dialect_id_string, section=None):
    '''The grammar features of a chosen dialect, in tree format '''
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
        if section:
            view_name = 'dialects:dialect-grammar-section'
            args.append(section)
        return HttpResponseRedirect(reverse(view_name, args=args))

    is_bulk_edit = request.GET.get('edit') or False
    base_dialect_id = int(request.GET.get('base_on', 0))
    if is_bulk_edit and base_dialect_id:
        dialect_ids.append(base_dialect_id)

    preserved    = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(dialect_ids)])
    dialects     = Dialect.objects.filter(id__in=dialect_ids).order_by(preserved)
    chosen_root  = get_section_root(section)

    # annotated lists are an efficient way of getting a big chunk of a treebeard tree
    # see: https://django-treebeard.readthedocs.io/en/latest/api.html#treebeard.models.Node.get_annotated_list
    max_depth    = chosen_root.depth + 1 if is_bulk_edit else None
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


    base_path = chosen_root.path if chosen_root else ''
    feature_examples = DialectFeature.objects.filter(dialect__in=dialect_ids) \
                                             .filter(feature__path__startswith=base_path) \
                                             .values('id', 'dialect_id', 'feature_id', 'feature__path', 'feature__fullheading',
                                                     'is_absent', 'introduction', 'comment', 'category',
                                                     'entries__id', 'entries__entry', 'entries__frequency', 'entries__comment') \
                                             .order_by('feature__path')

    if is_bulk_edit:  # Only provide examples at one level for bulk edit (can't bulk edit in subfolders)
        feature_examples = feature_examples.filter(feature__depth=max_depth)

    """
    Step *backwards* through the list of features `feature_list` trying to join in matching
    DialectFeature details from `feature_examples`.

    `feature_list` (FL) entries are tuples like:
       (<Feature object>, {**info about feature's position in hirarchy, see above link})
    `feature_examples` (FE) entries are dicts like:
       {'id': _, 'feature_id': _, 'feature__path': _, 'entries__entry': _}

    We match on Feature.path, if a match is found we port some uesful details from (FE) into
    the info entry in (FL)

    Much of the complexity is down to keeping track of whether a parent feature contains any
    children (or childrens-children, etc...) which have an entry. `entry_level` and `empty_level`
    are there to bubble entries (or a lack thereof) up the tree. As we traverse up a level we
    stamp the parent with an indicator of its deep contents to make rendering easier.
    """

    num_features = 0
    if len(feature_examples):
        entry_level = 0  # tracks presence of features with an entry up the tree
        empty_level = 0  # does the same for those with an entry
        i = len(feature_examples) - 1
        for j in range(len(feature_list) - 1, -1, -1):
            level = feature_list[j][1]['level']
            # If we've stepped up from where an entry was, mark the containing folder
            if level < entry_level:
                feature_list[j][1]['has_entry'] = True
                entry_level = level

            # If we've stepped up from where an empty was, mark the containing folder
            if level < empty_level:
                feature_list[j][1]['has_empty'] = True
                empty_level = level

            feature_id = feature_examples[i]['feature_id']
            if feature_list[j][0].id == feature_id:
                num_features += 1
                entry_level = level

                examples = OrderedDict((x, {}) for x in dialect_ids)
                while True:  # Loop through all examples of this feature
                    example = feature_examples[i]
                    if 'entries' not in examples[example['dialect_id']]:
                        examples[example['dialect_id']] = {
                            'id':                   example['id'],
                            'dialect_id':           example['dialect_id'],
                            'feature__fullheading': example['feature__fullheading'],
                            'is_absent':            example['is_absent'],
                            'introduction':         example['introduction'],
                            'comment':              example['comment'],
                            'category':             example['category'],
                            'entries':              [],
                        }
                    examples[example['dialect_id']]['entries'].append({
                        'id':        example['entries__id'],
                        'entry':     example['entries__entry'] or '',
                        'frequency': example['entries__frequency'],
                        'comment':   example['entries__comment'] or '',
                    })
                    i -= 1
                    if i < 0 or feature_examples[i]['feature_id'] != feature_id:
                        feature_list[j][1].update({
                            'dialects': examples
                        })
                        i = max(0, i)  # stop i from going negative
                        break
            else:
                if 'has_entry' not in feature_list[j][1]:
                    empty_level = level
                    feature_list[j][1]['has_empty'] = True

    context = {
        'dialect_ids':  dialect_ids,
        'dialects':     dialects,
        'section':      chosen_root,
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
        for feature, info in feature_list[1:]:
            if 'dialects' not in info:
                raw_rows.append('')
                continue

            dialect_idx = 1 if base_dialect_id else 0
            dialect     = info['dialects'][dialects[dialect_idx].id]
            entries     = dialect['entries'] if 'entries' in dialect else []
            raw_rows.append(' ~ '.join([encode_entry(x) for x in entries]))

        raw_text = '\n'.join(raw_rows)
        context.update({
            'raw_text':     raw_text,
            'example_text': 'kaθu  P "he writes" ~ kaθ <span style="color:red">M</span>',
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
            'entries': DialectFeatureEntry.objects.filter(feature=context['object'].id)
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
           .values_list('entry', 'feature__dialect_id', 'feature_id')[0:3]
        ) for type, regex in types
    ]

    cantfix = DialectFeatureEntry.objects
    for type, regex in types:
        cantfix = cantfix.exclude(entry__iregex=regex)
    cantfix = cantfix.values_list('entry', 'feature__dialect_id', 'feature_id')
    context = {
        'canfix': canfix,
        'cantfix': cantfix[0:1000],
        'cantfix_count': cantfix.count(),
    }
    return render(request, 'dialects/problems.html', context)
