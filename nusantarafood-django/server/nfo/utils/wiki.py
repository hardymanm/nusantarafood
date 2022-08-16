import wikipedia
import re


def scrape_wikipedia(title, lang):
    try:
        wikipedia.set_lang(lang)
        return wikipedia.summary(title, sentences=4)

    except wikipedia.PageError:
        print('Not found in {}.wikipedia'.format(lang))
        return ''


def extract_summary(summary, default_summary):
    pattern = r'(ialah|adalah|merupakan|merangkumi|kepada|makanan|consist |is a |consisting |made|is an )(.+?)[+,.;]'
    matches = re.findall(pattern, summary)
    regex_dot_matches = [match[1].strip() for match in matches]

    if len(regex_dot_matches) > 0:
        return ' '.join(regex_dot_matches)

    return default_summary


def get_wiki_summary(recipe, lang, default_summary):
    summary = scrape_wikipedia(recipe, lang)
    return extract_summary(summary, default_summary)