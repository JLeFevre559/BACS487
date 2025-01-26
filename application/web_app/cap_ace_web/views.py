from django.views.generic import TemplateView
from .models import MultipleChoice, MultipleChoiceDistractor
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView, ListView


User = get_user_model()

class Index(TemplateView):
    template_name = "index.html"

class LearningDetailView(TemplateView):
    template_name = 'learndash/detail.html'
    # model = Photo
    # context_object_name = 'photo'

class UserCreateView(CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = 'account/create.html'
    success_url = reverse_lazy('user_detail')
    
    def get_success_url(self):
        return reverse_lazy('user_detail', kwargs={'pk': self.object.pk})

class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'account/detail.html'
    context_object_name = 'user'

class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = CustomUserChangeForm
    template_name = 'account/edit.html'
    success_url = reverse_lazy('user_detail')
    
    def get_success_url(self):
        return reverse_lazy('user_detail', kwargs={'pk': self.object.pk})

class UserListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'account/list.html'
    context_object_name = 'users'

class UserDeleteView(LoginRequiredMixin, DeleteView):
    model = User
    template_name = 'account/delete.html'
    success_url = reverse_lazy('user_list')