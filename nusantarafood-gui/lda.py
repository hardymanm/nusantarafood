import re
import nltk
from nltk.corpus import wordnet
import gensim
from sklearn.feature_extraction.text import CountVectorizer

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


def make_LDAmodel(contents, num_topics, passes):
    vect = CountVectorizer(token_pattern='(?u)\\b\\w\\w\\w+\\b')
    X = vect.fit_transform(contents)
    corpus = gensim.matutils.Sparse2Corpus(X, documents_columns=False)

    id_map = dict((v, k) for k, v in vect.vocabulary_.items())

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
