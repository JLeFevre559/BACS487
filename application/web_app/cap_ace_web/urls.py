# example/urls.py
from django.urls import path, include
from .views import (
    Index,
)
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", Index.as_view(), name="Index"),
]
