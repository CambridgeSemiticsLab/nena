from rest_framework import viewsets
from .serializers import DialectListSerializer, DialectDetailSerializer

from dialects.models import Dialect


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

