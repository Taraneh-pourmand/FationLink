from functools import lru_cache
from pathlib import Path
import joblib

ML_DIR = Path(__file__).resolve().parent.parent / "ml"

@lru_cache(maxsize=1)
def _load():
    model = joblib.load(ML_DIR / "yelp_model.joblib")
    vec = joblib.load(ML_DIR / "yelp_vectorizer.joblib")
    return model, vec

def predict_sentiment(text):
    if not text or not text.strip():
        return None
    try:
        model, vec = _load()
        return model.predict(vec.transform([text]))[0]
    except Exception:
        return None
