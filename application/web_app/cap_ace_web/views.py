from django.views.generic import TemplateView
from .models import MultipleChoice, MultipleChoiceDistractor, QuestionProgress, CATEGORIES
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .forms import CustomUserCreationForm, CustomUserChangeForm, StockTickerForm, MultipleChoiceForm, MultipleChoiceDistractorFormSet
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView, ListView
from django.db.models import Count
from django.contrib import messages
from django.shortcuts import redirect


# Financial Data Feed Dashbaord View



User = get_user_model()

class Index(TemplateView):
    template_name = "home_dashboard.html"



class learningview(LoginRequiredMixin, TemplateView):
    template_name = 'customizelearning.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get current user
        user = self.request.user
        
        # Get all available questions per category
        total_questions = {
            category[0]: MultipleChoice.objects.filter(category=category[0]).count()
            for category in CATEGORIES
        }
        
        # Get completed questions for the user by category
        completed_questions = (
            QuestionProgress.objects
            .filter(user=user)
            .values('category')
            .annotate(completed=Count('question_id'))
        )
        
        # Calculate progress for each category
        categories = {}
        XP_PER_LEVEL = 140
        MAX_LEVEL = 30
        
        # Mapping for category codes to user XP fields
        xp_field_mapping = {
            'BUD': 'budget_xp',
            'INV': 'investing_xp',
            'SAV': 'savings_xp',
            'BAL': 'balance_sheet_xp',
            'CRD': 'credit_xp',
            'TAX': 'taxes_xp',
        }
        
        for category_code, category_name in CATEGORIES:
            # Get number of completed questions for this category
            completed = next(
                (item['completed'] for item in completed_questions 
                 if item['category'] == category_code),
                0
            )
            
            total = total_questions.get(category_code, 0)
            
            # Get XP directly from the user model
            xp_field = xp_field_mapping.get(category_code)
            xp = getattr(user, xp_field, 0) if xp_field else 0
            
            # Calculate level and progress based on XP
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
    
class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff

class MultipleChoiceListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = MultipleChoice
    template_name = 'multiple_choice/list.html'
    context_object_name = 'questions'
    ordering = ['category', 'difficulty']

class MultipleChoiceDetailView(LoginRequiredMixin, StaffRequiredMixin, DetailView):
    model = MultipleChoice
    template_name = 'multiple_choice/detail.html'
    context_object_name = 'question'

class MultipleChoiceCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = MultipleChoice
    form_class = MultipleChoiceForm
    template_name = 'multiple_choice/form.html'
    success_url = reverse_lazy('multiple_choice_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['distractor_formset'] = MultipleChoiceDistractorFormSet(self.request.POST)
        else:
            context['distractor_formset'] = MultipleChoiceDistractorFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        distractor_formset = context['distractor_formset']
        
        if distractor_formset.is_valid():
            self.object = form.save()
            distractor_formset.instance = self.object
            distractor_formset.save()
            messages.success(self.request, 'Multiple choice question created successfully.')
            return redirect(self.success_url)
        else:
            return self.render_to_response(self.get_context_data(form=form))

class MultipleChoiceUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = MultipleChoice
    form_class = MultipleChoiceForm
    template_name = 'multiple_choice/form.html'
    success_url = reverse_lazy('multiple_choice_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['distractor_formset'] = MultipleChoiceDistractorFormSet(
                self.request.POST, instance=self.object
            )
        else:
            context['distractor_formset'] = MultipleChoiceDistractorFormSet(
                instance=self.object
            )
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        distractor_formset = context['distractor_formset']
        
        if distractor_formset.is_valid():
            self.object = form.save()
            distractor_formset.instance = self.object
            distractor_formset.save()
            messages.success(self.request, 'Multiple choice question updated successfully.')
            return redirect(self.success_url)
        else:
            return self.render_to_response(self.get_context_data(form=form))

class MultipleChoiceDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = MultipleChoice
    template_name = 'multiple_choice/delete.html'
    success_url = reverse_lazy('multiple_choice_list')
    context_object_name = 'question'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Multiple choice question deleted successfully.')
        return super().delete(request, *args, **kwargs)
    
def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        password_confirm = request.POST['password_confirm']
        
        if password != password_confirm:
            messages.error(request, "Passwords do not match.")
            return render(request, 'registration/register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, 'registration/register.html')

        user = User.objects.create_user(username=username, password=password)
        user.save()

        # Automatically log the user in
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Redirect to home or dashboard
        
    return render(request, 'registration/register.html')

def bad_request(request, exception=None):
    return render(request, 'errors/400.html', status=400)

def permission_denied(request, exception=None):
    return render(request, 'errors/403.html', status=403)

def page_not_found(request, exception=None):
    return render(request, 'errors/404.html', status=404)

def server_error(request):
    return render(request, 'errors/500.html', status=500)

def method_not_allowed(request, exception=None):
    return render(request, 'errors/405.html', status=405)

def too_many_requests(request, exception=None):
    return render(request, 'errors/429.html', status=429)