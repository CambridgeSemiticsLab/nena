from rest_framework import viewsets
from .serializers import DialectListSerializer, DialectDetailSerializer, GrammarFeatureSerializer

from dialects.models import Dialect
from grammar.models import Feature


class DialectViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows dialects to be viewed or edited.
    """
    queryset = Dialect.objects.all()

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
    serializer_class = GrammarFeatureSerializer
