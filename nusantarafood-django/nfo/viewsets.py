from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework import pagination

from nfo import serializers, models


class StandardResultsSetPagination(pagination.PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000


class StopwordViewSet(viewsets.ModelViewSet):
    queryset = models.Stopword.objects.all()
    serializer_class = serializers.StopwordSerializer
    permission_classes = [permissions.IsAuthenticated]


class TabelViewSet(viewsets.ModelViewSet):
    queryset = models.Tabel.objects.all()
    serializer_class = serializers.TabelSerializer
    permission_classes = [permissions.IsAuthenticated]


class DatasetViewSet(viewsets.ModelViewSet):
    queryset = models.Dataset.objects.all()
    serializer_class = serializers.DatasetSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = models.Document.objects.all()
    serializer_class = serializers.DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]


class FoodCategoryViewSet(viewsets.ModelViewSet):
    queryset = models.FoodCategory.objects.all()
    serializer_class = serializers.FoodCategorySerializer
    permission_classes = [permissions.IsAuthenticated]


class WordViewSet(viewsets.ModelViewSet):
    queryset = models.Word.objects.all()
    serializer_class = serializers.WordSerializer
    permission_classes = [permissions.IsAuthenticated]


class JudgeSessionViewSet(viewsets.ModelViewSet):
    queryset = models.JudgeSession.objects.all()
    serializer_class = serializers.JudgeSessionSerializer
    permission_classes = [permissions.IsAuthenticated]


class WordnetAnswerViewSet(viewsets.ModelViewSet):
    queryset = models.WordnetAnswer.objects.all()
    serializer_class = serializers.WordnetAnswerSerializer
    permission_classes = [permissions.IsAuthenticated]


class WikiAnswerViewSet(viewsets.ModelViewSet):
    queryset = models.WikiAnswer.objects.all()
    serializer_class = serializers.WikiAnswerSerializer
    permission_classes = [permissions.IsAuthenticated]


class TabelAnswerViewSet(viewsets.ModelViewSet):
    queryset = models.TabelAnswer.objects.all()
    serializer_class = serializers.TabelAnswerSerializer
    permission_classes = [permissions.IsAuthenticated]
