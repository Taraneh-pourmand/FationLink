import pandas as pd
import joblib
df = pd.read_csv("data/fraud/creditcard.csv")
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix


x = df.drop("Class", axis=1)
y = df["Class"]

X_train, X_test, y_train, y_test = train_test_split(
    x,
    y,
    test_size=0.2,
    random_state=42,
    stratify = y
    
 )

model = RandomForestClassifier(
    n_estimators=100,
    class_weight="balanced",
    n_jobs=-1,
    random_state=42
    
 )
model.fit(X_train, y_train)

pred = model.predict(X_test)






print(confusion_matrix(y_test, pred))
print(classification_report(y_test, pred, digits=3))
print(y_train.value_counts())
print(y_test.value_counts())


joblib.dump(model, "ml/fraud_model.joblib")
