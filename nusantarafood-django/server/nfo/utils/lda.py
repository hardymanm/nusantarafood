import json
import re
import nltk
import gensim
import pyLDAvis
import pyLDAvis.gensim_models
from sklearn.feature_extraction.text import CountVectorizer

nltk.download('omw')
nltk.download('omw-1.4')


class Lda:
    document_list = []

    def __init__(self, document_objects, stopwords=[]):
        document_list = to_document_list(document_objects)
        document_list = remove_long_sentences(document_list)
        document_list = remove_number(document_list)
        document_list = remove_stopwords(document_list, stopwords)
        self.document_list = document_list

    def run(self, num_topics, passes):
        vect = CountVectorizer(token_pattern='(?u)\\b\\w\\w\\w+\\b')
        X = vect.fit_transform(self.document_list)
        corpus = gensim.matutils.Sparse2Corpus(X, documents_columns=False)

        id_map = dict((v, k) for k, v in vect.vocabulary_.items())
        word_map = dict((k, v) for k, v in vect.vocabulary_.items())

        model = gensim.models.ldamodel.LdaModel(corpus, num_topics=num_topics, passes=passes, random_state=0, id2word=id_map,
                                                chunksize=100, alpha='auto', per_word_topics=True, minimum_probability=1E-9)

        d = gensim.corpora.Dictionary()
        d.id2token = id_map
        d.token2id = word_map

        # to_json returns string of string. Remove first layer of json
        return json.loads(pyLDAvis.gensim_models.prepare(model, corpus, d).to_json())


# Helper functions
def to_document_list(document_objects):
    return [d.content for d in document_objects.iterator()]


# Helper functions
def remove_long_sentences(corpus_list, max_word=20):
    results = []
    for corpus in corpus_list:
        short_sentences = []
        for sentence in corpus.split('.'):
            if len(re.findall(r'\w+', sentence)) < max_word:
                short_sentences.append(sentence)

        results.append('. '.join(short_sentences))

    return results


# Helper functions
def remove_number(document_list):
    return [re.sub(r'\d+', '', corpus) for corpus in document_list]


# Helper functions
def remove_stopwords(corpus_list, stopwords):
    result = []
    for corpus in corpus_list:
        # match words, commas, and periods
        tokens = re.findall(r'\w+|[,.]', corpus)

        clean = []
        for token in tokens:
            if token not in stopwords:
                clean.append(token)

        corpus = ' '.join(clean)

        # remove space before comma: 'then , ' => 'then, '
        corpus = re.sub('\s[,]', ',', corpus)
        # remove space before period: 'done . ' => 'done. '
        corpus = re.sub('\s[.]', '.', corpus)

        result.append(corpus)

    return result
