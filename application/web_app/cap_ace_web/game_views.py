from django.views.generic import TemplateView
from .models import MultipleChoice, MultipleChoiceDistractor, QuestionProgress, FillInTheBlank
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .forms import CustomUserCreationForm, CustomUserChangeForm, StockTickerForm, MultipleChoiceForm, MultipleChoiceDistractorFormSet, FillInTheBlankForm
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView, ListView
from django.db.models import Count
from django.contrib import messages
from django.shortcuts import redirect



class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff
    
# Fill in the Blank Views
class FillInTheBlankListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = FillInTheBlank
    template_name = 'fill_blank/list.html'
    context_object_name = 'question'
    ordering = ['difficulty']

class FillInTheBlankDetailView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = FillInTheBlank
    template_name = 'fill_blank/detail.html'
    context_object_name = 'question'
    
class FillInTheBlankCreateView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = FillInTheBlank
    form_class = FillInTheBlankForm
    template_name = 'fill_blank/create.html'
    success_url = reverse_lazy('fill_blank_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['form'] = FillInTheBlankForm(self.request.POST)
        else:
            context['form'] = FillInTheBlankForm()
        return context

# Multiple Choice Views
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