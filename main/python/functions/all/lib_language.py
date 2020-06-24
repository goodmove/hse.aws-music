import nltk
from nltk.corpus import stopwords
import string


def to_lemmas(raw_text):
    table = str.maketrans('', '', string.punctuation)

    tokens = nltk.tokenize.word_tokenize(raw_text)
    tokens = [token.lower().translate(table) for token in tokens]
    words = [word.lower() for word in tokens if word.isalpha()]

    eng_stop_words = set(stopwords.words('english'))
    lemmatizer = nltk.WordNetLemmatizer()

    lemmas = [lemmatizer.lemmatize(word) for word in words if word not in eng_stop_words]

    return lemmas


def build_vocab(lemmas):
    vocab = dict()

    for w in lemmas:
        vocab[w] = vocab.get(w, 0) + 1

    return vocab


def build_vocab_from_text(text):
    return build_vocab(to_lemmas(text))
