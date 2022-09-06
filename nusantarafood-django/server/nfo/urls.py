from django.urls import path

from nfo import views

urlpatterns = [
    path('', views.index, name='home'),

    path('dataset', views.DatasetList.as_view(), name='dataset-list'),
    path('dataset/<int:pk>', views.DatasetDetail.as_view(), name='dataset-detail'),
    path('dataset/lda/<int:pk>', views.DatasetLdaDetail.as_view(), name='dataset-lda-detail'),

    path('dataset/regex-playground', views.RegexPlayground.as_view(), name='regex-playground'),

    path('dataset/task/lda/<int:pk>', views.run_lda_task, name='dataset-lda-create'),
    path('dataset/task/wordnet/<int:pk>', views.run_wordnet_task, name='dataset-run-wordnet-task'),
    path('dataset/task/wiki/<int:pk>', views.run_wiki_task, name='dataset-run-wiki-task'),
    path('dataset/task/tabel/<int:pk>', views.run_tabel_task, name='dataset-run-tabel-task'),

    path('dataset/document/<int:pk>', views.DocumentDetail.as_view(), name='document-detail'),
    path('dataset/import', views.upload_jlfile, name='dataset-upload'),
    path('dataset/delete/<int:pk>', views.DatasetDelete.as_view(), name='dataset-delete'),

    path('manage/judge', views.JudgeList.as_view(), name='judge-list'),
    path('manage/judge/<int:pk>', views.JudgeDetail.as_view(), name='judge-detail'),

    path('judge-wordnet', views.JudgeWordnetList.as_view(), name='judge-wordnet'),
    path('judge-wiki', views.JudgeWikiList.as_view(), name='judge-wiki'),
    path('judge-tabel', views.JudgeTabelList.as_view(), name='judge-tabel'),

    path('judge-wordnet/<int:pk>', views.JudgeWordnetInstruction.as_view(), name='judge-wordnet-instruction'),
    path('judge-wordnet/<int:pk>/item', views.JudgeWordnetItem.as_view(), name='judge-wordnet-item'),
    path('judge-wordnet/item/<int:pk>/answer', views.update_wordnet_answer, name='judge-wordnet-answer'),
    path('judge-wordnet/<int:pk>/done', views.JudgeWordnetDone.as_view(), name='judge-wordnet-done'),

    path('judge-wiki/<int:pk>', views.JudgeWikiInstruction.as_view(), name='judge-wiki-instruction'),
    path('judge-wiki/<int:pk>/item', views.JudgeWikiItem.as_view(), name='judge-wiki-item'),
    path('judge-wiki/item/<int:pk>/answer', views.update_wiki_answer, name='judge-wiki-answer'),
    path('judge-wiki/<int:pk>/done', views.JudgeWikiDone.as_view(), name='judge-wiki-done'),

    path('judge-tabel/<int:pk>', views.JudgeTabelInstruction.as_view(), name='judge-tabel-instruction'),
    path('judge-tabel/<int:pk>/item', views.JudgeTabelItem.as_view(), name='judge-tabel-item'),
    path('judge-tabel/item/<int:pk>/answer', views.update_tabel_answer, name='judge-tabel-answer'),
    path('judge-tabel/<int:pk>/done', views.JudgeTabelDone.as_view(), name='judge-tabel-done'),
]
