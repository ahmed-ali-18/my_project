import os
from pathlib import Path

import joblib
import nltk
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from .data_preprocessing import preprocess_text


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "complaints_training.csv"
MODEL_PATH = BASE_DIR / "ai" / "model.joblib"


def load_dataset():
    df = pd.read_csv(DATA_PATH)
    df["title"] = df["title"].fillna("")
    df["description"] = df["description"].fillna("")
    df["text"] = df["title"] + " " + df["description"]
    df["text_clean"] = df["text"].apply(preprocess_text)
    return df[["text_clean", "category"]]


def ensure_nltk_data():
    """Download required NLTK data if not already present."""
    for resource in ("punkt", "stopwords", "wordnet"):
        nltk.download(resource, quiet=True)


def train():
    ensure_nltk_data()
    df = load_dataset()
    X_train, X_test, y_train, y_test = train_test_split(
        df["text_clean"],
        df["category"],
        test_size=0.2,
        random_state=42,
        stratify=df["category"],
    )

    pipeline = Pipeline(
        [
            ("tfidf", TfidfVectorizer(max_features=5000, ngram_range=(1, 2))),
            ("clf", LogisticRegression(max_iter=200)),
        ]
    )

    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)
    print(classification_report(y_test, y_pred))

    os.makedirs(MODEL_PATH.parent, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")


if __name__ == "__main__":
    train()

