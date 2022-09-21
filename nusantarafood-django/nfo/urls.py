from django.urls import path, include
from rest_framework import routers

from nfo import viewsets, views

router = routers.DefaultRouter()
router.register(r'tokenlist', viewsets.TokenListViewSet)
router.register(r'tabels', viewsets.TabelViewSet)
router.register(r'datasets', viewsets.DatasetViewSet)
router.register(r'documents', viewsets.DocumentViewSet)
router.register(r'food-categories', viewsets.FoodCategoryViewSet)
router.register(r'words', viewsets.WordViewSet)
router.register(r'judge-sessions', viewsets.JudgeSessionViewSet)
router.register(r'wordnet-answers', viewsets.WordnetAnswerViewSet)
router.register(r'wiki-answers', viewsets.WikiAnswerViewSet)
router.register(r'tabel-answers', viewsets.TabelAnswerViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('accounts/', include('django.contrib.auth.urls')),

    path('utils/', views.ingredient_dataentry, name='utils-ingredient-dataentry'),

    path('', views.home, name='home'),
    path('manage/dataset', views.ManageDatasetList.as_view(), name='manage-dataset-list'),
    path('manage/dataset/<int:pk>', views.ManageDatasetDetail.as_view(), name='manage-dataset-detail'),
    path('manage/dataset/<int:pk>/delete', views.ManageDatasetDelete.as_view(), name='manage-dataset-delete'),
    path('manage/dataset/<int:pk>/rename', views.rename_dataset, name='manage-dataset-rename'),
    path('manage/dataset/<int:pk>/split', views.split_dataset, name='manage-dataset-split'),
    path('manage/dataset/<int:pk>/join', views.join_dataset, name='manage-dataset-join'),
    path('manage/dataset/<int:pk>/lda', views.ManageDatasetLda.as_view(), name='manage-dataset-lda-vis'),
    path('manage/dataset/<int:pk>/ontology/wordnet', views.ManageDatasetWordnetOntology.as_view(), name='manage-dataset-wordnet-ontology'),
    path('manage/dataset/<int:pk>/ontology/wiki', views.ManageDatasetWikiOntology.as_view(), name='manage-dataset-wiki-ontology'),
    path('manage/dataset/<int:pk>/ontology/tabel', views.ManageDatasetTabelOntology.as_view(), name='manage-dataset-tabel-ontology'),

    path('manage/dataset/<int:pk>/ontology/wordnet/json', views.download_wordnet_ontology_json, name='manage-dataset-wordnet-ontology-json'),
    path('manage/dataset/<int:pk>/ontology/wiki/json', views.download_wiki_ontology_json, name='manage-dataset-wiki-ontology-json'),
    path('manage/dataset/<int:pk>/ontology/tabel/json', views.download_tabel_ontology_json, name='manage-dataset-tabel-ontology-json'),

    path('manage/dataset/upload', views.upload_dataset, name='manage-dataset-upload'),
    path('manage/dataset/wiki/upload', views.upload_dataset_wiki, name='manage-dataset-wiki-upload'),
    path('manage/dataset/lda/upload', views.upload_dataset_lda, name='manage-dataset-lda-upload'),
    path('manage/dataset/word/upload', views.upload_dataset_word, name='manage-dataset-word-upload'),

    path('manage/dataset/document/<int:pk>', views.ManageDocumentDetail.as_view(), name='manage-document-detail'),

    path('manage/judge', views.ManageJudgeList.as_view(), name='manage-judge-list'),
    path('manage/judge/<int:pk>', views.ManageJudgeDetail.as_view(), name='manage-judge-detail'),

    path('judge-wordnet', views.JudgeWordnetList.as_view(), name='judge-wordnet'),
    path('judge-wordnet/<int:pk>', views.JudgeWordnetInstruction.as_view(), name='judge-wordnet-instruction'),
    path('judge-wordnet/<int:pk>/item', views.JudgeWordnetItem.as_view(), name='judge-wordnet-item'),
    path('judge-wordnet/item/<int:pk>/answer', views.update_wordnet_answer, name='judge-wordnet-answer'),
    path('judge-wordnet/<int:pk>/done', views.JudgeWordnetDone.as_view(), name='judge-wordnet-done'),

    path('judge-wiki', views.JudgeWikiList.as_view(), name='judge-wiki'),
    path('judge-wiki/<int:pk>', views.JudgeWikiInstruction.as_view(), name='judge-wiki-instruction'),
    path('judge-wiki/<int:pk>/item', views.JudgeWikiItem.as_view(), name='judge-wiki-item'),
    path('judge-wiki/item/<int:pk>/answer', views.update_wiki_answer, name='judge-wiki-answer'),
    path('judge-wiki/<int:pk>/done', views.JudgeWikiDone.as_view(), name='judge-wiki-done'),

    path('judge-tabel', views.JudgeTabelList.as_view(), name='judge-tabel'),
    path('judge-tabel/<int:pk>', views.JudgeTabelInstruction.as_view(), name='judge-tabel-instruction'),
    path('judge-tabel/<int:pk>/item', views.JudgeTabelItem.as_view(), name='judge-tabel-item'),
    path('judge-tabel/item/<int:pk>/answer', views.update_tabel_answer, name='judge-tabel-answer'),
    path('judge-tabel/<int:pk>/done', views.JudgeTabelDone.as_view(), name='judge-tabel-done'),

]
