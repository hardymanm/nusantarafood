from django.urls import path
from nfo import views

urlpatterns = [
    path('', views.index),
    path('contact-us', views.index),
    path('contribute', views.index),
    path('login', views.index),
    
    path('judge-wordnet', views.JudgeWordnetList.as_view(), name='judge-wordnet'),
    path('judge-wiki', views.JudgeWikiList.as_view(), name='judge-wiki'),
    path('judge-tabel', views.JudgeTabelList.as_view(), name='judge-tabel'),
    
    path('judge-wordnet/<int:pk>', views.JudgeWordnetInstruction.as_view(), name='judge-wordnet-instruction'),
    path('judge-wordnet/<int:pk>/item/<int:page>', views.judge_wordnet_item, name='judge-wordnet-item'),
]
