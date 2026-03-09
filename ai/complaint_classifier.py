import os

import joblib
from flask import current_app

from .data_preprocessing import preprocess_text


_model = None


def init_model(app=None):
    global _model
    flask_app = app or current_app
    try:
        model_path = flask_app.config["MODEL_PATH"]
        if os.path.exists(model_path):
            _model = joblib.load(model_path)
            flask_app.logger.info(f"Loaded complaint classifier from {model_path}")
        else:
            flask_app.logger.warning(
                "Complaint classifier model file not found; using rule-based fallback."
            )
    except Exception as exc:
        flask_app.logger.error(f"Error loading complaint classifier: {exc}")
        _model = None


RULES = {
    "road": "Road Issues",
    "pothole": "Road Issues",
    "garbage": "Garbage Management",
    "trash": "Garbage Management",
    "waste": "Garbage Management",
    "water": "Water Supply",
    "tap": "Water Supply",
    "lighting": "Street Lighting",
    "street light": "Street Lighting",
    "lamp": "Street Lighting",
    "drain": "Drainage Issues",
    "sewage": "Drainage Issues",
}


def rule_based_category(text: str) -> str:
    t = (text or "").lower()
    for kw, cat in RULES.items():
        if kw in t:
            return cat
    return "Garbage Management"


def classify_complaint(title: str, description: str):
    text = f"{title or ''} {description or ''}"
    clean = preprocess_text(text)

    if _model is None:
        category = rule_based_category(text)
        return category, 0.5

    proba = _model.predict_proba([clean])[0]
    classes = list(_model.classes_)
    idx = int(proba.argmax())
    return classes[idx], float(proba[idx])

