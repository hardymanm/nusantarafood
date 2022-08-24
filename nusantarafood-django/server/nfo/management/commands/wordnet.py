import re
import json
from django.core.management.base import BaseCommand
from django.db import transaction

import nltk
from nltk.corpus import wordnet
import gensim
from sklearn.feature_extraction.text import CountVectorizer

from nfo.models import Dataset, Document, LdaModel, Word
from nfo.utils.pylda import load_stopwords, make_LDAmodel


DEFAULT_PASSES = 20
DEFAULT_TOPIC_COUNT = 1
DEFAULT_LANGUAGE = "zsm"
NUM_WORD_OUTPUT = 30


def get_word_list(lda_model, num_words):
    result = []
    for i, topic in lda_model.show_topics(formatted=False, num_words=num_words):
        print('Topic:', i+1)
        for word, probability in topic:
            print(word.ljust(20), probability)
            result.append(word)
        print('----------------')

    return result


def remove_duplicate(hypernyms):
    names = set()
    output = []
    for h in hypernyms:
        if h['name'] not in names:
            output.append(h)
            names.add(h['name'])
    return output


def get_name_and_definition(hypernym):
    name = hypernym.lemma_names()[0]
    definition = hypernym.definition()
    return {'name': name, 'definition': definition}


def scrape_hypernym(word, language):
    synsets = wordnet.synsets(word, lang=language)
    hypernyms = []
    for s in synsets:
        hypernyms += [get_name_and_definition(h) for h in s.hypernyms()]

    hypernyms = remove_duplicate(hypernyms)

    return word, hypernyms


class Command(BaseCommand):
    # $ python manage.py wordnet -i aziekitchen-udang -s /home/amir/assets/stopwords.txt -t 7 -p 20
    def add_arguments(self, parser):
        parser.add_argument('-i', '--input-dataset', type=str, help='default summary if empty')
        parser.add_argument('-s', '--stopwords', type=str, help='default summary if empty')
        parser.add_argument('-t', '--num-topics', type=int, help='default summary if empty', default=DEFAULT_TOPIC_COUNT)
        parser.add_argument('-p', '--passes', type=int, help='default summary if empty', default=DEFAULT_PASSES)
        parser.add_argument('-l', '--lang', type=str, help='wordnet language. default=zsm', default=DEFAULT_LANGUAGE)

    def handle(self, *args, **kwargs):
        dataset_name = kwargs['input_dataset']
        stopwords_filename = kwargs['stopwords']
        num_topics = kwargs['num_topics']
        passes = kwargs['passes']
        lang = kwargs['lang']

        dataset = Dataset.objects.filter(name=dataset_name).first()
        documents = Document.objects.filter(dataset=dataset).all()
        stopwords = load_stopwords(stopwords_filename)

        lda_model, lda_data = make_LDAmodel(documents, stopwords, num_topics, passes)
        word_list = get_word_list(lda_model, NUM_WORD_OUTPUT)
        word_list_with_hypernyms = [scrape_hypernym(word, lang) for word in word_list]

        with transaction.atomic():
            lda = LdaModel(name=dataset_name, dataset=dataset, stopwords='\n'.join(stopwords), num_topics=num_topics, passes=passes, data=lda_data.to_json())
            lda.save()
            for w, hypernyms in word_list_with_hypernyms:
                json_hypernyms = json.dumps(hypernyms)
                word, _ = Word.objects.get_or_create(lda_model=lda, noun=w, hypernym=json_hypernyms)
                word.save()
