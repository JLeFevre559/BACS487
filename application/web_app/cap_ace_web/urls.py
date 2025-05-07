# example/urls.py
from django.urls import path, include
from .views import  (Index, UserListView, UserCreateView, UserDetailView, UserUpdateView, UserDeleteView, HomeView,learningview,
                    MultipleChoiceListView, MultipleChoiceDetailView, MultipleChoiceCreateView, MultipleChoiceUpdateView, MultipleChoiceDeleteView)
from django.contrib.auth import views as auth_views
from django.contrib import admin
from .import views 
from .game_views import  (MultipleChoiceGameView, BudgetSimulationGameView, FillInTheBlankCreateView, FillInTheBlankDeleteView, FillInTheBlankDetailView, FillInTheBlankListView, 
                          FillInTheBlankGameView, FlashCardGameView)
from .category_views import BudgetView, SavingsView, InvestingView, TaxesView, CreditView, BalanceSheetView
from django.views.generic import TemplateView

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
     path('register/', views.register, name='register'),
    
    
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

    # Play a multiple choice game
    path('learn/<str:category>/multiplechoice/', MultipleChoiceGameView.as_view(), name='play_multiple_choice'),

    # Play a flash card game (new)
    path('learn/<str:category>/flashcard/', FlashCardGameView.as_view(), name='play_flash_card'),

    
    #Play a Fill in the Blank game
    path('learn/<str:category>/fill-blank/', FillInTheBlankGameView.as_view(), name='play_fill_blank'),
    
    
    # # paths to Fill in the Blank games
    # path('fill-blank/', FillInTheBlankListView.as_view(), name='fill_blank_list'),
    # path('fill-blank/create/', FillInTheBlankCreateView.as_view(), name='fill_blank_create'),
    # path('fill-blank/<int:pk>/', FillInTheBlankDetailView.as_view(), name='fill_blank_detail'),

    path('learn/<str:category>/budgetsimulation/', BudgetSimulationGameView.as_view(), name='play_budget_simulation'),
    path('learn/<str:category>/budgetsimulation/<str:difficulty>/', BudgetSimulationGameView.as_view(), name='play_budget_simulation_difficulty'),

    # Temporary path for prod.
    path('learn/<str:category>/match-drag/', TemplateView.as_view(template_name='status/under_development.html'), name='play_match_drag'),
    # Special status pages
    path('under-development/', 
         TemplateView.as_view(template_name='status/under_development.html'), 
         name='under_development'),
    path('maintenance/', 
         TemplateView.as_view(template_name='status/maintenance.html'), 
         name='maintenance'),
    
    # For testing status pages during development
    path('status/200/', 
         TemplateView.as_view(template_name='errors/200.html'), 
         name='status_200'),
    path('status/404/', 
         views.page_not_found, 
         name='status_404'),
    path('status/500/', 
         views.server_error, 
         name='status_500'),
]