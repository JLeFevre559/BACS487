# example/urls.py
from django.urls import path, include
from .views import  Index, UserListView, UserCreateView, UserDetailView, UserUpdateView, UserDeleteView, HomeView,learningview
from django.contrib.auth import views as auth_views
from django.contrib import admin
from .import views
from .category_views import BudgetView, SavingsView, InvestingView, TaxesView, CreditView, BalanceSheetView

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
    
    
    # Paths to Learning Category pages where users can navigate to learning games 
    path('learn/budget/', BudgetView.as_view(), name='learn_budget'),
    path('learn/savings/', SavingsView.as_view(), name='learn_savings'),
    path('learn/investing/', InvestingView.as_view(), name='learn_investing'),
    path('learn/taxes/', TaxesView.as_view(), name='learn_taxes'),
    path('learn/credit/', CreditView.as_view(), name='learn_credit'),
    path('learn/balance/', BalanceSheetView.as_view(), name='learn_balance'),
]
