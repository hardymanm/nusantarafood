from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from nfo import views

urlpatterns = [
    path('recipes/', views.RecipeList.as_view()),
    path('recipes/<int:pk>/', views.RecipeDetail.as_view(), name='recipe-detail'),
    
    path('words/', views.WordList.as_view()),
    path('words/<int:pk>/', views.WordDetail.as_view(), name='word-detail'),
    
    path('datasets/', views.DatasetList.as_view()),
    path('datasets/<int:pk>/', views.DatasetDetail.as_view(), name='dataset-detail'),
    
    path('documents/', views.DocumentList.as_view()),
    path('documents/<int:pk>/', views.DocumentDetail.as_view(), name='document-detail'),
    
    path('food-categories/', views.FoodCategoryList.as_view()),
    path('food-categories/<int:pk>/', views.FoodCategoryDetail.as_view(), name='foodcategory-detail'),
    
    path('lda-models/', views.LdaModelList.as_view()),
    path('lda-models/<int:pk>/', views.LdaModelDetail.as_view(), name='ldamodel-detail'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
