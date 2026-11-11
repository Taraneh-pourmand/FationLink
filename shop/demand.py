from pathlib import Path
from datetime import timedelta
import joblib
from django.db.models import Sum
from django.db.models.functions import TruncWeek
from django.utils import timezone
from .models import OrderItem

MODEL = Path(__file__).resolve().parent.parent / "ml" / "demand_model.joblib"
_model = None

def forecast_next_week(product):
    global _model
    try:
        if _model is None:
            _model = joblib.load(MODEL)
        rows = (OrderItem.objects.filter(product=product)
                .annotate(w=TruncWeek("order__created_at")).values("w")
                .annotate(q=Sum("quantity")).order_by("-w")[:2])
        q = [r["q"] for r in rows]
        if len(q) < 2:
            return None
        nxt = timezone.now() + timedelta(weeks=1)
        X = [[q[0], q[1], nxt.month, nxt.isocalendar()[1]]]
        return max(0, round(float(_model.predict(X)[0])))
    except Exception:
        return None
