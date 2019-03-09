import json
from collections import OrderedDict

from django.shortcuts import render
from django.http import JsonResponse, Http404, HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.db.models import Case, When, F
from django.forms import modelform_factory, inlineformset_factory

from dialects.models import Dialect, DialectFeature, DialectFeatureEntry
from grammar.models import Feature
from gallery.models import Photo


def homepage(request):
    dialects = Dialect.objects.filter(longitude__isnull=False, latitude__isnull=False) \
                              .values('id', 'name', 'community', 'longitude', 'latitude')

    map_data = [dialect_to_map_point(d) for d in dialects]
    context = {
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

    def get_context_data(self, **kwargs):
        context = super(DialectListView, self).get_context_data(**kwargs)
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

# @staff_member_required
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

    preserved   = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(dialect_ids)])
    dialects    = Dialect.objects.filter(id__in=dialect_ids).order_by(preserved)
    chosen_root = get_section_root(section)

    # annotated lists are an efficient way of getting a big chunk of a treebeard tree
    # see: https://django-treebeard.readthedocs.io/en/latest/api.html#treebeard.models.Node.get_annotated_list
    feature_list = Feature.get_annotated_list(parent=chosen_root)

    base_path = chosen_root.path if chosen_root else ''
    feature_examples = DialectFeature.objects.filter(dialect__in=dialect_ids) \
                                             .filter(feature__path__startswith=base_path) \
                                             .values('id', 'dialect_id', 'feature_id', 'feature__path', 'entries__entry') \
                                             .order_by('feature__path')

    # Step *backwards* through the list of features `feature_list` trying to join in matching
    # DialectFeature details from `feature_examples`.
    #
    # `feature_list` (FL) entries are tuples like:
    #    (<Feature object>, {**info about feature's position in hirarchy, see above link})
    # `feature_examples` (FE) entries are dicts like:
    #    {'id': _, 'feature_id': _, 'feature__path': _, 'entries__entry': _}
    #
    # We match on Feature.path, if a match is found we port some uesful details from (FE) into
    # the info entry in (AL)
    #
    # Much of the complexity is down to keeping track of whether a parent feature contains any
    # children (or childrens-children, etc...) which have an entry. `entry_level` and `empty_level`
    # are there to bubble entries (or a lack thereof) up the tree. As we traverse up a level we
    # stamp the parent with an indicator of its deep contents to make rendering easier.
    #
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

                examples = OrderedDict((x, []) for x in dialect_ids)
                while True:  # Loop through all examples of this feature
                   # example_dialect_id = feature_examples[i]['dialect_id']
                    examples[feature_examples[i]['dialect_id']].append({
                        'text': feature_examples[i]['entries__entry'] or '-',
                        'df_id': feature_examples[i]['id'],
                   #     'dialect_id': example_dialect_id,
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
                                       .exclude(id__in=dialect_ids) \
                                       .values_list('id', 'name'),
    }

    if chosen_root:
        context['total_features'] = DialectFeature.objects.filter(dialect__in=dialect_ids).count()

    return render(request, 'grammar/feature_list.html', context)


class DialectFeatureDetailView(DetailView):

    name = 'DialectFeatureDetail'
    model = DialectFeature

    def get_context_data(self, **kwargs):
        context = super(DialectFeatureDetailView, self).get_context_data(**kwargs)
        context.update({
            'examples': DialectFeatureEntry.objects.filter(feature=context['object'].id)
        })
        return context


def dialect_feature_pane(request, dialect_id, feature_heading):
    """ renders just a snippet of html that contains details of the DialectFeature, for ajaxing
    """
    df = DialectFeature.objects.filter(dialect=dialect_id, feature__fullheading=feature_heading) \
                               .annotate(fullheading=F('feature__fullheading')) \
                               .first()
    context = {
        'dialect_id':      dialect_id,
        'feature_heading': feature_heading,
    }
    if df:
        # todo make feature_pane template expect dict in format of [Feature].entries to avoid
        # having to annotate for consistency with the data built in features_of_dialect() above
        # (which will also need changed!)
        context.update({
            'entries': df.entries.annotate(df_id=F('feature_id'), text=F('entry')),
        })
    return render(request, 'dialects/_dialectfeature_pane.html', context)


def dialect_feature_edit(request, dialect_id, feature_heading):
    """ and edit page for DialectFeature details as well as adding, changing and removing its examples
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
    df_form_class     = modelform_factory(DialectFeature, fields=('introduction', 'comment'))
    dfe_formset_class = inlineformset_factory(DialectFeature, DialectFeatureEntry,
                                              fields=('entry', 'frequency', 'comment'), extra=1)

    postvars    = request.POST or None
    df_form     = df_form_class(postvars, instance=df)
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
        ('penultiamte',      '^ *Regular assimilation of L-suffix and resulting gemination of \/[rn]\/\. *$'),
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
