# example/urls.py
from django.urls import path, include
from .views import  Index
from .views import HomeView
from .views import UserListView
from .views import UserCreateView
from .views import UserDetailView
from .views import UserUpdateView
from .views import UserDeleteView
from .views import learningview
from django.contrib.auth import views as auth_views
from django.contrib import admin
from .import views

urlpatterns = [
    path("", Index.as_view(), name="index"),
    path("", HomeView.as_view(), name="home"),
    path('users/', UserListView.as_view(), name='user_list'),
    path('users/create/', UserCreateView.as_view(), name='user_create'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user_detail'),
    path('users/<int:pk>/edit/', UserUpdateView.as_view(), name='user_edit'),
    path('users/<int:pk>/delete/', UserDeleteView.as_view(), name='user_delete'),
    path('admin/', admin.site.urls),
    path('users/', include('django.contrib.auth.urls')),
    path('learn/', learningview.as_view(), name='learn'),

]
