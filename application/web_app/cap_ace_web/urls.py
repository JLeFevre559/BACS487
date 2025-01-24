# example/urls.py
from django.urls import path, include
from .views import (
    Index, LearningDetailView
)
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", Index.as_view(), name="Index"),
    path('learningdash/detail',   LearningDetailView.as_view(),     name='learning_home'),





]
