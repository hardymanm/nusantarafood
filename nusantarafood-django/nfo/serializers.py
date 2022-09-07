from drf_queryfields import QueryFieldsMixin
from rest_framework import serializers
from nfo import models


class StopwordSerializer(QueryFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Stopword
        fields = '__all__'


class TabelSerializer(QueryFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Tabel
        fields = '__all__'


class DatasetSerializer(QueryFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Dataset
        fields = '__all__'


class DocumentSerializer(QueryFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Document
        fields = '__all__'


class FoodCategorySerializer(QueryFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = models.FoodCategory
        fields = '__all__'


class WordSerializer(QueryFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Word
        fields = '__all__'


class JudgeSessionSerializer(QueryFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = models.JudgeSession
        fields = '__all__'


class WordnetAnswerSerializer(QueryFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = models.WordnetAnswer
        fields = '__all__'


class WikiAnswerSerializer(QueryFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = models.WikiAnswer
        fields = '__all__'


class TabelAnswerSerializer(QueryFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = models.TabelAnswer
        fields = '__all__'
