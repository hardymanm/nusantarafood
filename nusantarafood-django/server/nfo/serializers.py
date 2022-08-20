import json
from rest_framework import serializers

from nfo import models


class JsonField(serializers.Field):

    def to_representation(self, value):
        return json.loads(value)

    def to_internal_value(self, data):
        return json.dumps(data)


class DatasetSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Dataset
        fields = '__all__'


class DocumentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Document
        fields = '__all__'


class FoodCategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.FoodCategory
        fields = '__all__'


class LdaModelSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.LdaModel
        fields = '__all__'


class RecipeSerializer(serializers.HyperlinkedModelSerializer):

    generated_categories = FoodCategorySerializer(many=True, read_only=True)

    class Meta:
        model = models.Recipe
        fields = ['url', 'dataset', 'document', 'title', 'definition_id', 'definition_ms', 'definition_en', 'generated_categories']


class WordSerializer(serializers.HyperlinkedModelSerializer):
    hypernyms = JsonField(source='hypernym')

    class Meta:
        model = models.Word
        fields = ['url', 'lda_model', 'noun', 'hypernyms']
