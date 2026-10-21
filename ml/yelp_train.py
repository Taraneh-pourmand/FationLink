import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix

mapping = {0: "negative", 1: "negative", 3: "positive", 4: "positive"}


def prepare(path, n):
    df = pd.read_csv(path)
    df["sentiment"] = df["label"].map(mapping)
    df = df.dropna(subset=["sentiment"])
    df = df.sample(n=n, random_state=42)
    return df


train = prepare("data/reviews/yelp_train.csv", 100000)
test = prepare("data/reviews/yelp_test.csv", 20000)

print(train["sentiment"].value_counts())
print(test["sentiment"].value_counts())
print(train.shape, test.shape)

vectorizer = TfidfVectorizer(max_features=50000, stop_words="english")
X_train = vectorizer.fit_transform(train["text"])
X_test = vectorizer.transform(test["text"])

y_train = train["sentiment"]
y_test = test["sentiment"]

model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

pred = model.predict(X_test)
print(confusion_matrix(y_test, pred))
print(classification_report(y_test, pred, digits=3))

joblib.dump(model, "ml/yelp_model.joblib")
joblib.dump(vectorizer, "ml/yelp_vectorizer.joblib")