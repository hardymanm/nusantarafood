from django.urls import path
from nfo import views

urlpatterns = [
    path('', views.index, name='home'),
    path('contact-us', views.index),
    path('contribute', views.index),
    path('login', views.index),
    
    path('test', views.generate_ldamodel, name='test'),
    
    path('dataset', views.DatasetList.as_view(), name='dataset-list'),
    path('dataset/<int:pk>', views.DatasetDetail.as_view(), name='dataset-detail'),
    
    path('judge-wordnet', views.JudgeWordnetList.as_view(), name='judge-wordnet'),
    path('judge-wiki', views.JudgeWikiList.as_view(), name='judge-wiki'),
    path('judge-tabel', views.JudgeTabelList.as_view(), name='judge-tabel'),
    
    path('judge-wordnet/<int:pk>', views.JudgeWordnetInstruction.as_view(), name='judge-wordnet-instruction'),
    path('judge-wordnet/<int:pk>/item/<int:page>', views.judge_wordnet_item, name='judge-wordnet-item'),
    path('judge-wordnet/<int:pk>/done', views.JudgeWordnetDone.as_view(), name='judge-wordnet-done'),
     
    path('judge-wiki/<int:pk>', views.JudgeWikiInstruction.as_view(), name='judge-wiki-instruction'),
    path('judge-wiki/<int:pk>/item/<int:page>', views.judge_wiki_item, name='judge-wiki-item'),
    path('judge-wiki/<int:pk>/done', views.JudgeWikiDone.as_view(), name='judge-wiki-done'),
        
    path('judge-tabel/<int:pk>', views.JudgeTabelInstruction.as_view(), name='judge-tabel-instruction'),
    path('judge-tabel/<int:pk>/item/<int:page>', views.judge_tabel_item, name='judge-tabel-item'),
    path('judge-tabel/<int:pk>/done', views.JudgeTabelDone.as_view(), name='judge-tabel-done'),
]
