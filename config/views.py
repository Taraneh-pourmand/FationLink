from django.http import HttpResponse
import joblib  
from django.conf import settings


def home(request):
    return HttpResponse("Welcome to FationLink babe!")


vectorizer_path = settings.BASE_DIR / "ml"/ "yelp_vectorizer.joblib"

model_path = settings.BASE_DIR /"ml"/"yelp_model.joblib"


vectorizer = joblib.load(vectorizer_path) 
model = joblib.load(model_path)
