import numpy as np
from sklearn.ensemble import IsolationForest
from .models import Order


def fraud_orders():
    orders = list(Order.objects.prefetch_related("items"))
    if len(orders) < 20:
        return []
    X = np.array([
        [float(o.total),
         sum(i.quantity for i in o.items.all()),
         o.created_at.hour]
        for o in orders
    ])
    labels = IsolationForest(contamination=0.05, random_state=0).fit_predict(X)
    return [o for o, l in zip(orders, labels) if l == -1]