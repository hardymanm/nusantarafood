import re
from django.conf import settings

stopwords = []
with open(settings.BASE_DIR / 'stopwords.txt', 'r') as f:
    stopwords = f.read().splitlines()


def clean_title(title):
    title = title.lower()                   # lowercase
    words = re.findall('[A-Za-z]+', title)   # alphabet only
    clean = filter(lambda w: w not in stopwords, words)  # remove stopwords
    return ' '.join(clean)
