import re
from string import punctuation

import nltk
from nltk import word_tokenize
from nltk.corpus import stopwords


class ContentUtil:

    @staticmethod
    def preprocess_sentence(text):
        stop_words = set(stopwords.words('english'))
        # stop_words.extend(['from', 'subject', 're', 'edu', 'use','figure', 'fig'])
        # stemmer = SnowballStemmer("english")
        lem = nltk.stem.wordnet.WordNetLemmatizer()
        cleanr = re.compile('\[(.*?)\]')
        text = re.sub(cleanr, '', text)
        text = re.sub(r'http\S+', '', text)
        text = re.sub("[0-9]{2}", '', text)
        text = text.replace('/', ' ')
        text = text.replace('\'', ' \' ')
        pat = r'[^a-zA-z0-9.,!?/:;\"\'\s]'
        text = re.sub(pat, '', text)
        text = text.lower()

        # Tokenise the text - try with bert tokeniser later
        # words = word_tokenize(text)
        words = text.split()
        # text = ' '.join([stemmer.stem(word) for word in words])
        # words = [stemmer.stem(word) for word in words]
        text = ' '.join([lem.lemmatize(word) for word in words])
        # text = ' '.join(words)
        text = ' '.join([w for w in text.split() if len(w) > 1])
        text = text.replace('/`/', '')
        text = text.replace('/"/', '')
        text = text.replace("/'/", "")

        tokens = [token for token in word_tokenize(text) if token not in punctuation and token not in stop_words]
        return ' '.join(tokens)

    @staticmethod
    def preprocess_sentence_returns_list(text):
        stop_words = set(stopwords.words('english'))
        # stop_words.extend(['from', 'subject', 're', 'edu', 'use','figure', 'fig'])
        # stemmer = SnowballStemmer("english")
        lem = nltk.stem.wordnet.WordNetLemmatizer()
        cleanr = re.compile('\[(.*?)\]')
        text = re.sub(cleanr, '', text)
        text = re.sub(r'http\S+', '', text)
        text = re.sub("[0-9]{2}", '', text)
        text = text.replace('/', ' ')
        text = text.replace('\'', ' \' ')
        pat = r'[^a-zA-z0-9.,!?/:;\"\'\s]'
        text = re.sub(pat, '', text)
        text = text.lower()

        # Tokenise the text - try with bert tokeniser later
        # words = word_tokenize(text)
        words = text.split()
        # text = ' '.join([stemmer.stem(word) for word in words])
        # words = [stemmer.stem(word) for word in words]
        text = ' '.join([lem.lemmatize(word) for word in words])
        # text = ' '.join(words)
        text = ' '.join([w for w in text.split() if len(w) > 1])
        text = text.replace('/`/', '')
        text = text.replace('/"/', '')
        text = text.replace("/'/", "")

        tokens = [token for token in word_tokenize(text) if token not in punctuation and token not in stop_words]
        return tokens
