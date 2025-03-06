# example/urls.py
from django.urls import path, include
from .views import  (Index, UserListView, UserCreateView, UserDetailView, UserUpdateView, UserDeleteView, HomeView,learningview,
                    MultipleChoiceListView, MultipleChoiceDetailView, MultipleChoiceCreateView, MultipleChoiceUpdateView, MultipleChoiceDeleteView)
from django.contrib.auth import views as auth_views
from django.contrib import admin
from .import views 
from .game_views import FillInTheBlankListView, FillInTheBlankDetailView, FillInTheBlankCreateView
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

    # Paths to multiple choice games
    path('multiple-choice/', MultipleChoiceListView.as_view(), name='multiple_choice_list'),
    path('multiple-choice/<int:pk>/', MultipleChoiceDetailView.as_view(), name='multiple_choice_detail'),
    path('multiple-choice/create/', MultipleChoiceCreateView.as_view(), name='multiple_choice_create'),
    path('multiple-choice/<int:pk>/edit/', MultipleChoiceUpdateView.as_view(), name='multiple_choice_edit'),
    path('multiple-choice/<int:pk>/delete/', MultipleChoiceDeleteView.as_view(), name='multiple_choice_delete'),

    # paths to Fill in the Blank games
    path('fill-blank/', FillInTheBlankListView.as_view(), name='fill_blank_list'),
    path('fill-blank/create/', FillInTheBlankCreateView.as_view(), name='fill_blank_create'),
    path('fill-blank/<int:pk>/', FillInTheBlankDetailView.as_view(), name='fill_blank_detail'),

]
from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('', views.home, name='home'),  # Home route
]
