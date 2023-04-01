import re
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from nfo.models import Document


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        documents = Document.objects.all()
        users = User.objects.filter(groups__name='judge')
        for document in documents:
            for user in users:
                qs = document.tabelanswer_set.filter(judge=user)
                if qs.count() > 1:
                    merge_tabel_answer(qs)

                # qs = document.wikianswer_set.filter(judge=user)
                # if qs.count() > 1:
                #     merge_wiki_answer(qs)


def merge_tabel_answer(qs):
    correct_categories = []
    suggested_categories = ''
    count = 0
    for answer in qs.all():
        correct_categories += answer.correct_categories.all()
        if answer.suggested_categories and len(answer.suggested_categories) > 0:
            count += 1
            suggested_categories = answer.suggested_categories
            if count > 1:
                print(answer.pk)

    for answer in qs.all():
        if answer.dataset:
            answer.correct_categories.set(correct_categories)
            answer.suggested_categories = suggested_categories
            answer.save()
        else:
            answer.delete()


def merge_wiki_answer(qs):
    suggested_categories = ''
    count = 0
    for answer in qs.all():
        if answer.suggested_categories and len(answer.suggested_categories) > 0:
            count += 1
            suggested_categories = answer.suggested_categories
            # print(suggested_categories)
            if count > 1:
                print(answer.pk)

    for answer in qs.all():
        if answer.dataset:
            answer.suggested_categories = suggested_categories
            answer.save()
        else:
            answer.delete()