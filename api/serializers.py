from rest_framework import serializers
from dialects.models import Dialect
from grammar.models import Feature
from rest_framework_recursive.fields import RecursiveField

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

#    def to_representation(self, instance):
#        return {
#            'id': instance.id,
#            'type': 'Feature',
#            'geometry': {
#                'type': 'Point',
#                'coordinates': [
#                    instance.latitude,
#                    instance.longitude,
#                ]
#            },
#            'properties': {
#                'name': instance.name,
#                'url': '#',
#                'community': instance.community,
#                'class': 'group1' if instance.community == 'C' else 'group2',
#            },
#        } #if instance.latitude and instance.longitude else {}


class GrammarFeatureListSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serialise grammar feature objects
    """
    url = serializers.HyperlinkedIdentityField(view_name="api:feature-detail", read_only=True)
    type = serializers.CharField(source='nodetype', read_only=True)

    class Meta:
        model = Feature
        fields = ('id', 'type', 'fullheading','name', 'url', )
        read_only_fields = ('id', 'type', 'fullheading','name', 'url', )


class GrammarFeatureDetailSerializer(serializers.ModelSerializer):
    """
    Serialise grammar feature objects
    """
    children = GrammarFeatureListSerializer(many=True, read_only=True)
    type = serializers.CharField(source='nodetype', read_only=True)

    class Meta:
        model = Feature
        fields = ("id", "type", "name", "heading", "fullheading", "children", )
        read_only_fields = ("id", "type", "name", "heading", "fullheading", "children", )
