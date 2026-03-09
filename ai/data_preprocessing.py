import re

import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer


_lemmatizer = WordNetLemmatizer()
_stop_words = set(stopwords.words("english"))
_clean_re = re.compile(r"[^a-zA-Z\s]")


def preprocess_text(text: str) -> str:
    if not text:
        return ""
    text = text.lower()
    text = _clean_re.sub(" ", text)
    tokens = nltk.word_tokenize(text)
    tokens = [t for t in tokens if t not in _stop_words and len(t) > 2]
    tokens = [_lemmatizer.lemmatize(t) for t in tokens]
    return " ".join(tokens)

