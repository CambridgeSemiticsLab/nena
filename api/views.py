from django.shortcuts import get_object_or_404

from rest_framework import viewsets, filters
from django_filters import rest_framework as dfilters

from .serializers import DialectListSerializer, DialectDetailSerializer, GrammarFeatureListSerializer, GrammarFeatureDetailSerializer
from dialects.models import Dialect
from grammar.models import Feature

class DialectViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows dialects to be viewed or edited.
    """
    queryset = Dialect.objects.all()
    filter_backends = (dfilters.DjangoFilterBackend, filters.OrderingFilter)
    filter_fields = ('community', 'location')
    ordering_fields = ('name', 'country', 'location')

    def get_serializer_class(self):
        """
        Serialize to a less detailed view for list operations.
        """
        return DialectListSerializer if self.action == 'list' else DialectDetailSerializer


class GrammarFeatureViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows grammar features to be viewed or edited.
    """
    queryset = Feature.objects.all()

    def get_queryset(self):
        return Feature.objects.filter(depth__lte=2) if self.action == 'list' else Feature.objects.all()

    def get_serializer_class(self):
        """
        Serialize to a less detailed view for list operations.
        """
        return GrammarFeatureListSerializer if self.action == 'list' else GrammarFeatureDetailSerializer
