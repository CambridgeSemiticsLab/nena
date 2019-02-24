import json

from django.shortcuts import render
from django.http import JsonResponse, Http404
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from dialects.models import Dialect, DialectFeature, DialectFeatureEntry
from grammar.models import Feature


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
            'map_data_json': json.dumps(map_data, indent=2),
            'map_center': [self.object.longitude, self.object.latitude]
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

@staff_member_required
def features_of_dialect(request, dialect_id, section=None):
    '''The grammar features of a chosen dialect, in tree format '''
    dialect     = Dialect.objects.get(pk=dialect_id)
    chosen_root = get_section_root(section)

    # annotated lists are an efficient way of getting a big chunk of a treebeard tree
    # see: https://django-treebeard.readthedocs.io/en/latest/api.html#treebeard.models.Node.get_annotated_list
    feature_list = Feature.get_annotated_list(parent=chosen_root)

    base_path = chosen_root.path if chosen_root else ''
    feature_examples = DialectFeature.objects.filter(dialect=dialect) \
                                             .filter(feature__path__startswith=base_path) \
                                             .values('id', 'feature_id', 'feature__path', 'entries__entry') \
                                             .order_by('feature__path')

    # todo - entries__entry can bring in multiple rows per dialect feature, consider how to use below


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

            id = feature_examples[i]['feature_id']
            if feature_list[j][0].id == id:
                num_features += 1
                entry_level = level

                feature_list[j][1].update({
                    'entry': feature_examples[i]['entries__entry'] or '-',
                    'df_id': feature_examples[i]['id'],
                })

                while i > 0:  # skip over additional examples of same feature
                    i -= 1
                    if feature_examples[i]['feature_id'] != id:
                        break
            else:
                if 'has_entry' not in feature_list[j][1]:
                    empty_level = level
                    feature_list[j][1]['has_empty'] = True

    context = {
        'dialect':      dialect,
        'section':      chosen_root,
        'feature_list': feature_list,
        'num_features': num_features,
    }

    if chosen_root:
        context['total_features'] = DialectFeature.objects.filter(dialect=dialect).count()

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

