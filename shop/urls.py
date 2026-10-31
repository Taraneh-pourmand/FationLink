from django.urls import path

from . import views

app_name = "shop"

urlpatterns = [
    path("review/", views.review, name="review"),
    path("fraud/", views.fraud, name="fraud"),
]