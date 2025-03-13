from django.views.generic import TemplateView
from .models import MultipleChoice, MultipleChoiceDistractor, QuestionProgress, QUESTION_TYPES
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView, ListView
from django.db.models import Count

#Learning Category Views - Should we Make a new views.py file for the game specific views?

class BalanceSheetView(LoginRequiredMixin, TemplateView):
    template_name = "categories/balance_sheet.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        #completed Question by question Type?
        completed_questions = (
            QuestionProgress.objects
            .filter(user=self.request.user, category='BAL')
            .values('question_type')
            .annotate(completed=Count('question_id'))
        )

        learning_games = {}
            #Loop through for dashboard
        for game_code, game_name in QUESTION_TYPES:
            completed = next(
                (item['completed'] for item in completed_questions 
                 if item['question_type'] == game_code),
                0
            )

            url_mapping = {
                'MC': '/balance/multiplechoice/',
                'FIB': '/balance/fill-blank/',
                'MAD': '/balance/match-drag/',
                'FC': '/balance/flashcard/',
                'BS': '/balance/budgetsimulation/'
            }
            learning_games[game_code] = {
                'title': game_name,
                'url': '/learn' + url_mapping.get(game_code, '/'),
                
            }
        context.update({
            'learning_games': learning_games,
            
        })
        return context


class CreditView(LoginRequiredMixin, TemplateView):
    template_name = "categories/credit.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        #completed Question by question Type?
        completed_questions = (
            QuestionProgress.objects
            .filter(user=self.request.user, category='CRD')
            .values('question_type')
            .annotate(completed=Count('question_id'))
        )

        learning_games = {}
            #Loop through for dashboard
        for game_code, game_name in QUESTION_TYPES:
            completed = next(
                (item['completed'] for item in completed_questions 
                 if item['question_type'] == game_code),
                0
            )

            url_mapping = {
                'MC': '/credit/multiplechoice/',
                'FIB': '/credit/fill-blank/',
                'MAD': '/credit/match-drag/',
                'FC': '/credit/flashcard/',
                'BS': '/credit/budgetsimulation/'
            }
            learning_games[game_code] = {
                'title': game_name,
                'url': '/learn' + url_mapping.get(game_code, '/'),
                
            }
        context.update({
            'learning_games': learning_games,
            
        })
        return context




class TaxesView(LoginRequiredMixin, TemplateView):
    template_name = "categories/taxes.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        #completed Question by question Type?
        completed_questions = (
            QuestionProgress.objects
            .filter(user=self.request.user, category='TAX')
            .values('question_type')
            .annotate(completed=Count('question_id'))
        )

        learning_games = {}
            #Loop through for dashboard
        for game_code, game_name in QUESTION_TYPES:
            completed = next(
                (item['completed'] for item in completed_questions 
                 if item['question_type'] == game_code),
                0
            )

            url_mapping = {
                'MC': '/taxes/multiplechoice/',
                'FIB': '/taxes/fill-blank/',
                'MAD': '/taxes/match-drag/',
                'FC': '/taxes/flashcard/',
                'BS': '/taxes/budgetsimulation/'
            }
            learning_games[game_code] = {
                'title': game_name,
                'url': '/learn' + url_mapping.get(game_code, '/'),
                
            }
        context.update({
            'learning_games': learning_games,
            
        })
        return context




class InvestingView(LoginRequiredMixin, TemplateView):
    template_name = "categories/investing.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        #completed Question by question Type?
        completed_questions = (
            QuestionProgress.objects
            .filter(user=self.request.user, category='INV')
            .values('question_type')
            .annotate(completed=Count('question_id'))
        )

        learning_games = {}
            #Loop through for dashboard
        for game_code, game_name in QUESTION_TYPES:
            completed = next(
                (item['completed'] for item in completed_questions 
                 if item['question_type'] == game_code),
                0
            )

            url_mapping = {
                'MC': '/investing/multiplechoice/',
                'FIB': '/investing/fill-blank/',
                'MAD': '/investing/match-drag/',
                'FC': '/investing/flashcard/',
                'BS': '/investing/budgetsimulation/'
            }
            learning_games[game_code] = {
                'title': game_name,
                'url': '/learn' + url_mapping.get(game_code, '/'),
                
            }
        context.update({
            'learning_games': learning_games,
            
        })
        return context




class SavingsView(LoginRequiredMixin, TemplateView):
    template_name = "categories/savings.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        #completed Question by question Type?
        completed_questions = (
            QuestionProgress.objects
            .filter( user=self.request.user, category='SAV' )
            .values('question_type')
            .annotate(completed=Count('question_id'))
        )

        learning_games = {}
            #Loop through for dashboard
        for game_code, game_name in QUESTION_TYPES:
            completed = next(
                (item['completed'] for item in completed_questions 
                 if item['question_type'] == game_code),
                0
            )

            url_mapping = {
                'MC': '/savings/multiplechoice/',
                'FIB': '/savings/fill-blank/',
                'MAD': '/savings/match-drag/',
                'FC': '/savings/flashcard/',
                'BS': '/savings/budgetsimulation/'
            }
            learning_games[game_code] = {
                'title': game_name,
                'url': '/learn' + url_mapping.get(game_code, '/'),
                
            }
        context.update({
            'learning_games': learning_games,
            
        })
        return context

class BudgetView(LoginRequiredMixin, TemplateView):
    template_name = "categories/budget.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        #completed Question by question Type?
        completed_questions = (
            QuestionProgress.objects
            .filter(user=self.request.user, category='BUD')
            .values('question_type')
            .annotate(completed=Count('question_id'))
        )

        learning_games = {}
            #Loop through for dashboard
        for game_code, game_name in QUESTION_TYPES:
            print(game_code)
            completed = next(
                (item['completed'] for item in completed_questions 
                 if item['question_type'] == game_code),
                0
            )

            url_mapping = {
                'MC': '/budget/multiplechoice/',
                'FIB': '/budget/fill-blank/',
                'MAD': '/budget/match-drag/',
                'FC': '/budget/flashcard/',
                'BS': '/budget/budgetsimulation/'
            }
            learning_games[game_code] = {
                'title': game_name,
                'url': '/learn' + url_mapping.get(game_code, '/'),
                
            }
        context.update({
            'learning_games': learning_games,
            
        })
        return context

