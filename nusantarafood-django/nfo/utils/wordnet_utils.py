from nltk.corpus import wordnet

DEFAULT_LANGUAGE = "zsm"
NUM_WORD_OUTPUT = 30


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


def get_hypernyms(word, language):
    synsets = wordnet.synsets(word, lang=language)
    hypernyms = []
    for s in synsets:
        hypernyms += [get_name_and_definition(h) for h in s.hypernyms()]

    return remove_duplicate(hypernyms)
