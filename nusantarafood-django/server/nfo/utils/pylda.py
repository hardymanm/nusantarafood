import re
import nltk
from nltk.corpus import wordnet
import gensim
import pyLDAvis, pyLDAvis.gensim_models
from sklearn.feature_extraction.text import CountVectorizer


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
        if len(re.findall(r'\w+', sentence)) < max_word:
            short_sentences.append(sentence)

    return '. '.join(short_sentences)


def remove_number(content):
    return re.sub(r'\d+', '', content)


def remove_stopwords(content, stopwords):
    # @todo: has effect removing period. therefore we lose sentence
    # @todo: CountVectorizer has stop_words param. Use that instead?
    tokens = re.findall(r'\w+', content)
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
    word_map = dict((k, v) for k, v in vect.vocabulary_.items())

    model = gensim.models.ldamodel.LdaModel(corpus, num_topics=num_topics, passes=passes, random_state=0, id2word=id_map,
                                           chunksize=100, alpha='auto', per_word_topics=True, minimum_probability=1E-9)
    
    d = gensim.corpora.Dictionary()
    d.id2token = id_map
    d.token2id = word_map
    model_data = pyLDAvis.gensim_models.prepare(model, corpus, d)
    
    return model, model_data


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
