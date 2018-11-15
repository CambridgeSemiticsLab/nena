from rest_framework import serializers
from dialects.models import Dialect
from grammar.models import Feature

class DialectListSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializes dialects for list views, adding a URL for each item,
    but omitting potentially verbose fields.
    """
    url = serializers.HyperlinkedIdentityField(view_name="api:dialect-detail")

    class Meta:
        model = Dialect
        fields = ('url',
                  'name',
                  'community',
                  'country',
                  'location',
                  'latitude',
                  'longitude',
        )


class DialectDetailSerializer(serializers.ModelSerializer):
    """
    Serialize dialect objects for detail views, including all fields.
    """
    class Meta:
        model = Dialect
        fields = '__all__'


class GrammarFeatureSerializer(serializers.ModelSerializer):
    """
    Serialise grammar feature objects
    """
    class Meta:
        model = Feature
        fields = '__all__'
