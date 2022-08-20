import re
import json
from django.core.management.base import BaseCommand
from django.db import transaction

import nltk
from nltk.corpus import wordnet
import gensim
from sklearn.feature_extraction.text import CountVectorizer

from nfo.models import Dataset, Document, LdaModel, Word


DEFAULT_PASSES = 20
DEFAULT_TOPIC_COUNT = 1
DEFAULT_LANGUAGE = "zsm"
NUM_WORD_OUTPUT = 30

nltk.download('wordnet')
nltk.download('omw')
nltk.download('omw-1.4')


def load_stopwords(filename):
    stopwords = []
    with open(filename, 'r') as f:
        stopwords = f.read().splitlines()

    return stopwords


def remove_long_sentences(content, max_word=20):
    short_sentences = []
    for sentence in content.split('.'):
        if len(re.findall('\w+', sentence)) > max_word:
            short_sentences.append(sentence)

    return '. '.join(short_sentences)


def remove_number(content):
    return re.sub('\d+', '', content)


def remove_stopwords(content, stopwords):
    # @todo: has effect removing period. therefore we lose sentence
    # @todo: CountVectorizer has stop_words param. Use that instead?
    tokens = re.findall('\w+', content)
    clean = []
    for token in tokens:
        if token in stopwords:
            clean.append(token)

    return ' '.join(clean)


def make_LDAmodel(document_list, stopwords, num_topics, passes):
    content_list = [d.content for d in document_list]
    content_list = [remove_long_sentences(c) for c in content_list]
    content_list = [remove_number(c) for c in content_list]
    # content_list = [remove_stopwords(c, stopwords) for c in content_list]

    vect = CountVectorizer(token_pattern='(?u)\\b\\w\\w\\w+\\b', stop_words=stopwords)
    X = vect.fit_transform(content_list)
    corpus = gensim.matutils.Sparse2Corpus(X, documents_columns=False)

    id_map = dict((v, k) for k, v in vect.vocabulary_.items())
    # word_map = dict((k, v) for k, v in vect.vocabulary_.items())

    return gensim.models.ldamodel.LdaModel(corpus, num_topics=num_topics, passes=passes, random_state=0, id2word=id_map,
                                           chunksize=100, alpha='auto', per_word_topics=True, minimum_probability=1E-9)


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

        lda_model = make_LDAmodel(documents, stopwords, num_topics, passes)
        word_list = get_word_list(lda_model, NUM_WORD_OUTPUT)
        word_list_with_hypernyms = [scrape_hypernym(word, lang) for word in word_list]

        with transaction.atomic():
            lda = LdaModel(name=dataset_name, dataset=dataset, stopwords='\n'.join(stopwords), num_topics=num_topics, passes=passes)
            lda.save()
            for w, hypernyms in word_list_with_hypernyms:
                json_hypernyms = json.dumps(hypernyms)
                word, _ = Word.objects.get_or_create(lda_model=lda, noun=w, hypernym=json_hypernyms)
                word.save()
