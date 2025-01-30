from django.views.generic import TemplateView
from .models import MultipleChoice, MultipleChoiceDistractor
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
import yfinance as yf
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView, ListView


# Financial Data Feed Dashbaord View



User = get_user_model()

class Index(TemplateView):
    template_name = "index.html"


class HomeView(TemplateView):
    template_name = 'theme.html'
    def get_context_data(self, **kwargs):
        # Call the parent method to get any existing context
        context = super().get_context_data(**kwargs)

        # List of stock symbols you want to track
        stock_symbols = ['AAPL', 'GOOG', 'TSLA']

        # Dictionary to store stock data
        stocks = {}
        
        for symbol in stock_symbols:
            try:
                # Fetch stock data using yfinance
                stock = yf.Ticker(symbol)
                stock_info = stock.history(period='1d')  # Latest data for the day

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

class UserDeleteView(LoginRequiredMixin, SuperUserRequiredMixin, DeleteView):
    model = User
    template_name = 'account/delete.html'
    success_url = reverse_lazy('user_list')