# example/urls.py
from django.urls import path, include
from .views import (
    Index,
    UserListView, UserCreateView, UserDetailView, UserUpdateView, UserDeleteView,
)
from django.contrib.auth import views as auth_views
from django.contrib import admin

urlpatterns = [
    path("", Index.as_view(), name="index"),
    path('users/', UserListView.as_view(), name='user_list'),
    path('users/create/', UserCreateView.as_view(), name='user_create'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user_detail'),
    path('users/<int:pk>/edit/', UserUpdateView.as_view(), name='user_edit'),
    path('users/<int:pk>/delete/', UserDeleteView.as_view(), name='user_delete'),
    path('admin/', admin.site.urls),
    path('users/', include('django.contrib.auth.urls')),
]
