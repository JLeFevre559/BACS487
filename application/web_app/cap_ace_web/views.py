from django.views.generic import TemplateView
from .models import MultipleChoice, MultipleChoiceDistractor, QuestionProgress
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .forms import CustomUserCreationForm, CustomUserChangeForm, StockTickerForm
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView, ListView
from django.db.models import Count


# Financial Data Feed Dashbaord View



User = get_user_model()

class Index(TemplateView):
    template_name = "home_dashboard.html"

#GameViews - Should we Make a new views.py file for the game specific views?

class BalanceSheetView(LoginRequiredMixin, TemplateView):
    template_name = "categories/balance_sheet.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        #completed Question by question Type?
        completed_questions = (
            QuestionProgress.objects
            .filter(user=self.request.user)
            .values('question_type')
            .annotate(completed=Count('question_id'))
        )

        learning_games = {}
            #Loop through for dashboard
        for game_code, game_name in QuestionProgress.QUESTION_TYPES:
            completed = next(
                (item['completed'] for item in completed_questions 
                 if item['category'] == game_code),
                0
            )

            url_mapping = {
                'MC': '/balance-multiplechoice/',
                'FIB': '/balance-fill-blank/',
                'MAD': '/balance-match-drag/',
                'FC': '/balance-flashcard/',
                'BS': '/balance-budgetsimulation/'
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
            .filter(user=self.request.user)
            .values('question_type')
            .annotate(completed=Count('question_id'))
        )

        learning_games = {}
            #Loop through for dashboard
        for game_code, game_name in QuestionProgress.QUESTION_TYPES:
            completed = next(
                (item['completed'] for item in completed_questions 
                 if item['category'] == game_code),
                0
            )

            url_mapping = {
                'MC': '/credit-multiplechoice/',
                'FIB': '/credit-fill-blank/',
                'MAD': '/credit-match-drag/',
                'FC': '/credit-flashcard/',
                'BS': '/credit-budgetsimulation/'
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
            .filter(user=self.request.user)
            .values('question_type')
            .annotate(completed=Count('question_id'))
        )

        learning_games = {}
            #Loop through for dashboard
        for game_code, game_name in QuestionProgress.QUESTION_TYPES:
            completed = next(
                (item['completed'] for item in completed_questions 
                 if item['category'] == game_code),
                0
            )

            url_mapping = {
                'MC': '/taxes-multiplechoice/',
                'FIB': '/taxes-fill-blank/',
                'MAD': '/taxes-match-drag/',
                'FC': '/taxes-flashcard/',
                'BS': '/taxes-budgetsimulation/'
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
            .filter(user=self.request.user)
            .values('question_type')
            .annotate(completed=Count('question_id'))
        )

        learning_games = {}
            #Loop through for dashboard
        for game_code, game_name in QuestionProgress.QUESTION_TYPES:
            completed = next(
                (item['completed'] for item in completed_questions 
                 if item['category'] == game_code),
                0
            )

            url_mapping = {
                'MC': '/investing-multiplechoice/',
                'FIB': '/investing-fill-blank/',
                'MAD': '/investing-match-drag/',
                'FC': '/investing-flashcard/',
                'BS': '/investing-budgetsimulation/'
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
            .filter(user=self.request.user)
            .values('question_type')
            .annotate(completed=Count('question_id'))
        )

        learning_games = {}
            #Loop through for dashboard
        for game_code, game_name in QuestionProgress.QUESTION_TYPES:
            completed = next(
                (item['completed'] for item in completed_questions 
                 if item['category'] == game_code),
                0
            )

            url_mapping = {
                'MC': '/savings-multiplechoice/',
                'FIB': '/savings-fill-blank/',
                'MAD': '/savings-match-drag/',
                'FC': '/savings-flashcard/',
                'BS': '/savings-budgetsimulation/'
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
            .filter(user=self.request.user)
            .values('question_type')
            .annotate(completed=Count('question_id'))
        )

        learning_games = {}
            #Loop through for dashboard
        for game_code, game_name in QuestionProgress.QUESTION_TYPES:
            completed = next(
                (item['completed'] for item in completed_questions 
                 if item['category'] == game_code),
                0
            )

            url_mapping = {
                'MC': '/budget-multiplechoice/',
                'FIB': '/budget-fill-blank/',
                'MAD': '/budget-match-drag/',
                'FC': '/budget-flashcard/',
                'BS': '/budget-budgetsimulation/'
            }
            learning_games[game_code] = {
                'title': game_name,
                'url': '/learn' + url_mapping.get(game_code, '/'),
                
            }
        context.update({
            'learning_games': learning_games,
            
        })
        return context

class learningview(LoginRequiredMixin, TemplateView):
    template_name = 'customizelearning.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all available questions per category
        total_questions = {
            category[0]: MultipleChoice.objects.filter(category=category[0]).count()
            for category in QuestionProgress.CATEGORIES
        }
        
        # Get completed questions for the user by category
        completed_questions = (
            QuestionProgress.objects
            .filter(user=self.request.user)
            .values('category')
            .annotate(completed=Count('question_id'))
        )
        
        # Calculate progress for each category
        categories = {}
        XP_PER_QUESTION = 10
        XP_PER_LEVEL = 20
        MAX_LEVEL = 30
        
        for category_code, category_name in QuestionProgress.CATEGORIES:
            # Get number of completed questions for this category
            completed = next(
                (item['completed'] for item in completed_questions 
                 if item['category'] == category_code),
                0
            )
            
            total = total_questions.get(category_code, 0)
            
            # Calculate XP and level
            xp = completed * XP_PER_QUESTION
            level = min(xp // XP_PER_LEVEL, MAX_LEVEL)
            progress_to_next = (xp % XP_PER_LEVEL) / XP_PER_LEVEL * 100 if level < MAX_LEVEL else 100
            
            # Get completion percentage
            completion_percentage = (completed / total * 100) if total > 0 else 0
            
            # Create URL based on category code
            url_mapping = {
                'BUD': '/budget/',
                'INV': '/investing/',
                'SAV': '/savings/',
                'BAL': '/balance/',
                'CRD': '/credit/',
                'TAX': '/taxes/'
            }
            
            categories[category_code] = {
                'title': category_name,
                'url': '/learn' + url_mapping.get(category_code, '/'),
                'total_questions': total,
                'completed_questions': completed,
                'completion_percentage': round(completion_percentage, 1),
                'xp': xp,
                'level': level,
                'progress': round(progress_to_next, 1),
                'icon': f'{category_name.lower()}-icon'  # CSS class for the icon
            }
        
        # Calculate totals
        total_xp = sum(cat['xp'] for cat in categories.values())
        total_completed = sum(cat['completed_questions'] for cat in categories.values())
        
        context.update({
            'categories': categories,
            'total_xp': total_xp,
            'total_completed': total_completed
        })
        return context

class HomeView(TemplateView):
    template_name = 'theme.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Dictionary to store stock data
        stocks = {}
        # Initialize the form and get any user input from the GET request
        form = StockTickerForm(self.request.GET)
        context['form'] = form

        # Default stock symbols if no input is provided
        stock_symbols = ['AAPL', 'GOOG', 'TSLA']

        if form.is_valid():
            # If the form is valid, get tickers from the form input
            tickers_input = form.cleaned_data['tickers']
            stock_symbols = [ticker.strip().upper() for ticker in tickers_input.split(',')]
        
        for symbol in stock_symbols:
            try:
                # Fetch stock data using yfinance
                # stock = yf.Ticker(symbol)
                # stock_info = stock.history(period='1d')  # Latest data for the day
                stock_info = []

                # Check if the stock_info is not empty
                if not stock_info.empty:
                    latest_data = stock_info.iloc[-1]  # Get the latest row of data
                    stocks[symbol] = {
                        'close': latest_data['Close'],
                        'date': latest_data.name.strftime('%Y-%m-%d'),  # Convert datetime to string
                    }
                else:
                    stocks[symbol] = {'close': 'No data available', 'date': 'N/A'}
            except Exception as e:
                stocks[symbol] = {'close': f'Error fetching data: {e}', 'date': 'N/A'}

        # Add the stock data to the context
        context['stocks'] = stocks
        
        return context

class UserCreateView(CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = 'account/create.html'
    success_url = reverse_lazy('user_detail')
    
    def get_success_url(self):
        return reverse_lazy('user_detail', kwargs={'pk': self.object.pk})

class SuperUserRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser

class UserDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = User
    template_name = 'account/detail.html'
    context_object_name = 'user'

    def test_func(self):
        # Allow if superuser or if user is viewing their own profile
        return self.request.user.is_superuser or self.request.user.pk == self.get_object().pk

class UserUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = User
    form_class = CustomUserChangeForm
    template_name = 'account/edit.html'
    success_url = reverse_lazy('user_detail')
    
    def test_func(self):
        # Allow if superuser or if user is editing their own profile
        return self.request.user.is_superuser or self.request.user.pk == self.get_object().pk
    
    def get_success_url(self):
        return reverse_lazy('user_detail', kwargs={'pk': self.object.pk})

class UserListView(LoginRequiredMixin, SuperUserRequiredMixin, ListView):
    model = User
    template_name = 'account/list.html'
    context_object_name = 'users'

class UserDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = User
    template_name = 'account/delete.html'
    success_url = reverse_lazy('user_list')

    def test_func(self):
        # Allow if superuser or if user is editing their own profile
        return self.request.user.is_superuser or self.request.user.pk == self.get_object().pk