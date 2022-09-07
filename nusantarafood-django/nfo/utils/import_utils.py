import json

from nfo import models


def import_lda_data(file):
    dataset_name = file.name[9:-5] + '.jl'
    dataset = models.Dataset.objects.filter(name=dataset_name).first()
    if dataset:
        dataset.lda_data = file.read().decode()
        dataset.save()
    else:
        print('Failed:', dataset_name)


def import_lda_terms(file):
    dataset_name = file.name[9:-5] + '.jl'
    dataset = models.Dataset.objects.filter(name=dataset_name).first()

    terms_list = json.loads(file.read().decode())
    result = set()
    for terms in terms_list:
        for term in terms:
            result.add(term)

    if dataset:
        dataset.lda_terms = json.dumps(list(result))
        dataset.save()

        for term in list(result):
            word, _ = models.Word.objects.get_or_create(dataset=dataset, noun=term)

    else:
        print('Failed:', dataset_name)
