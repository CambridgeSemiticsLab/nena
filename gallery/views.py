from django.shortcuts import get_object_or_404

from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import reverse_lazy

from dialects.models import Dialect
from gallery.models import Photo

class PhotoListView(ListView):

    name = 'Photos'
    model = Photo
    context_object_name = 'photos'

    def get_context_data(self, **kwargs):
        context = super(PhotoListView, self).get_context_data(**kwargs)
        return context

class PhotoDetailView(DetailView):

    name = 'Photos'
    model = Photo

    def get_context_data(self, **kwargs):
        context = super(PhotoDetailView, self).get_context_data(**kwargs)
        return context

class DialectPhotoView(ListView):

    name = 'Photos'
    context_object_name = 'photos'

    def get_queryset(self):
        self.dialect = get_object_or_404(Dialect, pk=self.kwargs['dialect'])
        return Photo.objects.filter(dialect=self.dialect)

    def get_context_data(self, **kwargs):
        context = super(DialectPhotoView, self).get_context_data(**kwargs)
        context['dialect'] = self.dialect
        return context

@method_decorator(login_required, name='dispatch')
class PhotoCreateView(CreateView):
    model = Photo
    fields = '__all__'

@method_decorator(login_required, name='dispatch')
class PhotoUpdateView(UpdateView):
    model = Photo
    fields = '__all__'

@method_decorator(login_required, name='dispatch')
class PhotoDeleteView(DeleteView):
    model = Photo
    fields = '__all__'
    success_url = reverse_lazy('gallery:photo-list')

