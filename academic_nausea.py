import re
from nltk.corpus import stopwords
from nltk.stem.snowball import RussianStemmer
import os
from collections import Counter
from multiprocessing import Pool as ThreadPool
from stuff.task.database.database import add_data


def get_clean_words(text):

    """
    Get rid of stop-words and words, which len(word) <= 2
    :param text:
    :return: set of words
    """

    words = set()
    _stopwords = set(stopwords.words('russian'))
    regex = re.compile('[\-a-zа-яё]+', re.M | re.I)
    for word in [word.lower() for word in regex.findall(text) if len(word) > 2]:
        if word in _stopwords:
            continue
        words.add(word)
    return words


def validate(word):

    """
    Check latin in word
    :param word:
    :return: bool
    """

    if not word:
        return True

    is_fraud = False
    regex_rus = re.compile('[а-я\-ё]+', re.I)
    regex_eng = re.compile('[a-z\-]+', re.I)
    check = regex_rus.search(word)
    if check is None:
        check = regex_eng.search(word)
    if len(word) != len(check.group(0)):
        is_fraud = True
    return is_fraud


def word_normalizer(text):

    """
    Detect letter swap (rus-eng & vv)
    :param text:
    :return: list (text, is_fraud)
    """

    # еще была идея с сравнением ord'ов для каждого символа (и сравнением двух крайних от символа),
    # но, кажется, это муторно, да и работать будет дольше

    tokens = []
    is_fraud = False
    for word in text:
        if not is_fraud:
            is_fraud = all(map(validate, word.split('-')))
        tokens.append(RussianStemmer().stem(word))
    return tokens, is_fraud


def get_nausea(tokens, c=5):

    """
    :param tokens:
    :param c: number of popular tokens
    :return: ration (sum of frequency/number of tokens)
    """

    if not tokens:
        return 0
    token_freq = sorted(Counter(tokens).items(), key=lambda x: x[1], reverse=True)[:c]
    return sum([x[1] for x in token_freq]) / len(tokens)


def text_results(text_data):

    """
    Do all calculations
    :param text_data:
    :return: file name, ratio and fraud or not
    """

    fname, text = text_data
    clean_words = get_clean_words(text)
    tokens, is_fraud = word_normalizer(clean_words)
    nausea = get_nausea(tokens)
    return fname, nausea, is_fraud


def get_texts(path):

    """
    Collect all texts and file names
    :param path:
    :return: dict {fname: text}
    """

    data = []
    if path.endswith('txt'):
        fname = os.path.basename(path)
        with open(path) as f:
            text = f.read()
        data.append((fname, text))
        return data

    path += '/'
    for fname in os.listdir(path):
        if fname.endswith('txt'):
            with open(path + fname) as f:
                data.append((fname, f.read()))
    return data


if __name__ == '__main__':
    path = input('Enter a path to the files or to a file directly: ')
    texts = get_texts(path)
    pool = ThreadPool()
    print('Произвожу расчеты...')
    results = pool.map(text_results, texts)
    pool.close()
    pool.join()
    print('Сохраняю данные...')
    add_data(results)
    print('Сделяль :)')

