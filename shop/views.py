from pathlib import Path

import joblib
import pandas as pd
from django.conf import settings
from django.shortcuts import render

ML_DIR = Path(settings.BASE_DIR) / "ml"
yelp_model = joblib.load(ML_DIR / "yelp_model.joblib")
yelp_vectorizer = joblib.load(ML_DIR / "yelp_vectorizer.joblib")
fraud_model = joblib.load(ML_DIR / "fraud_model.joblib")
fraud_data = pd.read_csv(Path(settings.BASE_DIR) / "data" / "fraud" / "creditcard.csv")


def review(request):
    result = None
    text = ""
    if request.method == "POST":
        text = request.POST.get("text", "").strip()
        if text:
            X = yelp_vectorizer.transform([text])
            result = yelp_model.predict(X)[0]
    return render(request, "shop/review.html", {"result": result, "text": text})


def fraud(request):
    result = None
    if request.method == "POST":
        row = fraud_data.sample(n=1)
        actual = int(row["Class"].iloc[0])
        X = row.drop("Class", axis=1)
        prob = float(fraud_model.predict_proba(X)[0][1])
        result = {
            "amount": round(float(row["Amount"].iloc[0]), 2),
            "probability": round(prob * 100, 2),
            "predicted": "Fraud" if prob >= 0.5 else "Normal",
            "actual": "Fraud" if actual == 1 else "Normal",
        }
    return render(request, "shop/fraud.html", {"result": result})