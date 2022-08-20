from rest_framework import generics

from nfo import models, serializers


class RecipeList(generics.ListCreateAPIView):
    queryset = models.Recipe.objects.all()
    serializer_class = serializers.RecipeSerializer


class RecipeDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Recipe.objects.all()
    serializer_class = serializers.RecipeSerializer


class WordList(generics.ListCreateAPIView):
    queryset = models.Word.objects.all()
    serializer_class = serializers.WordSerializer


class WordDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Word.objects.all()
    serializer_class = serializers.WordSerializer


class DatasetList(generics.ListCreateAPIView):
    queryset = models.Dataset.objects.all()
    serializer_class = serializers.DatasetSerializer


class DatasetDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Dataset.objects.all()
    serializer_class = serializers.DatasetSerializer


class DocumentList(generics.ListCreateAPIView):
    queryset = models.Document.objects.all()
    serializer_class = serializers.DocumentSerializer


class DocumentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Document.objects.all()
    serializer_class = serializers.DocumentSerializer


class FoodCategoryList(generics.ListCreateAPIView):
    queryset = models.FoodCategory.objects.all()
    serializer_class = serializers.FoodCategorySerializer


class FoodCategoryDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.FoodCategory.objects.all()
    serializer_class = serializers.FoodCategorySerializer


class LdaModelList(generics.ListCreateAPIView):
    queryset = models.LdaModel.objects.all()
    serializer_class = serializers.LdaModelSerializer


class LdaModelDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.LdaModel.objects.all()
    serializer_class = serializers.LdaModelSerializer
