import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error



df = pd.read_csv("data/demand/online_retail_II.csv")
df = df[(df["Quantity"] > 0) & (df["Price"] > 0)]
df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
df["week"] = df["InvoiceDate"].dt.to_period("W").dt.start_time

weekly_sales = df.groupby("week") ["Quantity"].sum()
ws = weekly_sales.to_frame("sales")

ws["lag_1"] = ws["sales"].shift(1)
ws["lag_2"] = ws["sales"].shift(2)

ws["month"]= ws.index.month
ws["weekofyear"] = ws.index.isocalendar().week.astype(int)

ws = ws.dropna()

x = ws[["lag_1", "lag_2", "month", "weekofyear"]]
y = ws["sales"]

X_train = x.iloc[:-20]
X_test = x.iloc[-20:]

y_train = y.iloc[:-20]
y_test = y.iloc[-20:]


model = RandomForestRegressor(random_state=42)

model.fit(X_train, y_train)
import joblib
joblib.dump(model, "ml/demand_model.joblib")
pred = model.predict(X_test)


#print(X_train.shape, X_test.shape)
print("MAE model:", mean_absolute_error(y_test, pred))
print("MAE model:", mean_absolute_error(y_test, X_test["lag_1"]))

result = y_test.to_frame("real")
result["prediction"] = pred
result["error"] = (result["real"] - result["prediction"]).abs()
#print(result)
print(result.sort_values("error", ascending=False).head(5))
#print(x.head())
#print(y.head())

#print(ws.shape)
#print(ws.head()) 
#print(df.dtypes)
#print(df.isna().sum())
#print(df["Quantity"].describe()) 
#print(df["InvoiceDate"].dtype)
#print(df[["InvoiceDate", "week"]].head())
#print(weekly_sales)

model = RandomForestRegressor(
    n_estimators=200,
    random_state=0
)














