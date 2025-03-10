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
from django.shortcuts import get_object_or_404
import random
from django.views import View
from django.urls import reverse



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
    
    def form_valid(self, form):
        context = self.get_context_data()
        fill_form = context['form']
        
        if fill_form.is_valid():
            self.object = fill_form.save()
            fill_form.instance = self.object
            fill_form.save()
            messages.success(self.request, 'Fill in the Blank question created successfully.')
            return redirect(self.success_url)
        else:
            return self.render_to_response(self.get_context_data(form=form))
        

class FillInTheBlankDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = FillInTheBlank
    template_name = 'fill-blank/delete.html'
    success_url = reverse_lazy('fill_blank_list')
    context_object_name = 'question'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Fill in the Blank question deleted successfully.')
        return super().delete(request, *args, **kwargs)

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
    
class MultipleChoiceGameView(LoginRequiredMixin, View):
    template_name = 'multiple_choice/game.html'
    
    def get_random_question(self, category, user):
        """Get a random question from the specified category that the user hasn't completed"""
        category_mapping = {
            'budget': 'BUD',
            'investing': 'INV',
            'savings': 'SAV',
            'balance': 'BAL',
            'credit': 'CRD',
            'taxes': 'TAX',
        }
        category = category_mapping[category]
        # First, get all completed question IDs for this user and category
        completed_ids = QuestionProgress.objects.filter(
            user=user,
            question_type='MC',
            category=category
        ).values_list('question_id', flat=True)
        
        # Find questions in this category that haven't been completed
        available_questions = MultipleChoice.objects.filter(
            category=category
        ).exclude(
            id__in=completed_ids
        )
        
        # If there are no uncompleted questions, get all questions in this category
        if not available_questions.exists():
            available_questions = MultipleChoice.objects.filter(category=category)
            
        # If there are still no questions, return None
        if not available_questions.exists():
            return None
            
        # Select a random question
        question = random.choice(list(available_questions))
        return question
    
    def get(self, request, category):
        # Get a random question for this category
        question = self.get_random_question(category, request.user)
        
        if not question:
            messages.error(request, f"No questions available for this category.")
            return redirect('learn')
        
        # Get distractors and shuffle them with the correct answer
        distractors = list(question.distractors.values_list('distractor', flat=True))
        choices = distractors + [question.answer]
        random.shuffle(choices)
        
        context = {
            'question': question,
            'choices': choices,
            'category': question.get_category_display(),
            'category_code': category,
        }
        
        return render(request, self.template_name, context)
    
    def post(self, request, category):
        inp_category = category
        category_mapping = {
            'budget': 'BUD',
            'investing': 'INV',
            'savings': 'SAV',
            'balance': 'BAL',
            'credit': 'CRD',
            'taxes': 'TAX',
        }
        category = category_mapping[category]
        question_id = request.POST.get('question_id')
        selected_answer = request.POST.get('answer')
        
        question = get_object_or_404(MultipleChoice, id=question_id)
        
        # Check if the answer is correct
        is_correct = (selected_answer == question.answer)
        
        # If this is first time completing this question
        if is_correct:
            # Check if the question has already been completed
            _, created = QuestionProgress.objects.get_or_create(
                user=request.user,
                question_id=question_id,
                question_type='MC',
                category=category
            )
            
            # Only add XP if this is the first time completing the question
            if created:
                # Determine which XP field to update based on category
                xp_field_mapping = {
                    'BUD': 'budget_xp',
                    'INV': 'investing_xp',
                    'SAV': 'savings_xp',
                    'BAL': 'balance_sheet_xp',
                    'CRD': 'credit_xp',
                    'TAX': 'taxes_xp',
                }
                
                # Get the field name to update
                xp_field = xp_field_mapping.get(category)

                xp_mapping = {
                    'B': 50,
                    'I': 100,
                    'A': 150,
                }
                xp = xp_mapping.get(question.difficulty, 0)
                
                # Update the user's XP (add 10 XP per question)
                if xp_field:
                    user = request.user
                    current_xp = getattr(user, xp_field)
                    setattr(user, xp_field, current_xp + xp)
                    user.save(update_fields=[xp_field])
        
        context = {
            'question': question,
            'selected_answer': selected_answer,
            'is_correct': is_correct,
            'category_code': category,
            'next_url': reverse('play_multiple_choice', kwargs={'category': inp_category}),
            'home_url': reverse('learn'),
        }
        
        return render(request, 'multiple_choice/result.html', context)