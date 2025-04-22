from django.views.generic import TemplateView
from .models import MultipleChoice, MultipleChoiceDistractor, QuestionProgress, BudgetSimulation, Expense, FillInTheBlank
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
import json
from django.http import JsonResponse



class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff
    
# Fill in the Blank Views

class FillInTheBlankGameView(LoginRequiredMixin, View):
    template_name = 'fill_blank/game.html'
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
            question_type='FIB',
            category=category
        ).values_list('question_id', flat=True)
        
        # Find questions in this category that haven't been completed
        available_questions = FillInTheBlank.objects.filter(
            category=category
        ).exclude(
            id__in=completed_ids
        )
        
        # If there are no uncompleted questions, get all questions in this category
        if not available_questions.exists():
            available_questions = FillInTheBlank.objects.filter(category=category)
            
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
        
        context = {
            'question': question,
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
        selected_answer = request.POST.get('missing_word')
        
        question = get_object_or_404(FillInTheBlank, id=question_id)
        
        # Check if the answer is correct
        is_correct = (selected_answer == question.missing_word)
        
        # If this is first time completing this question
        if is_correct:
            # Check if the question has already been completed
            _, created = QuestionProgress.objects.get_or_create(
                user=request.user,
                question_id=question_id,
                question_type='FIB',
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
            'next_url': reverse('play_fill_blank', kwargs={'category': inp_category}),
            'home_url': reverse('learn'),
        }
        
        return render(request, 'multiple_choice/result.html', context)
    

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
    
class BudgetSimulationGameView(LoginRequiredMixin, View):
    template_name = 'budgetq/game.html'
    
    def get_random_simulation(self, user, category, difficulty=None):
        """Get a random budget simulation that the user hasn't completed"""
        # Map URL category to database category code
        category_mapping = {
            'budget': 'BUD',
            'investing': 'INV',
            'savings': 'SAV',
            'balance': 'BAL',
            'credit': 'CRD',
            'taxes': 'TAX',
        }
        db_category = category_mapping.get(category, 'BUD')
        
        # First, get all completed simulation IDs for this user
        completed_ids = QuestionProgress.objects.filter(
            user=user,
            question_type='BS',
            category=db_category
        ).values_list('question_id', flat=True)
        
        # Base query - find simulations for this category that haven't been completed
        query = BudgetSimulation.objects.filter(category=db_category).exclude(id__in=completed_ids)
        
        # Apply difficulty filter if specified
        if difficulty and difficulty in ['B', 'I', 'A']:
            query = query.filter(difficulty=difficulty)
            
        # If there are no uncompleted questions, get all questions for this category
        if not query.exists():
            query = BudgetSimulation.objects.filter(category=db_category)
            if difficulty and difficulty in ['B', 'I', 'A']:
                query = query.filter(difficulty=difficulty)
                
        # If there are still no questions, return None
        if not query.exists():
            return None
            
        # Select a random simulation
        simulation = random.choice(list(query))
        return simulation
    
    def get(self, request, category, difficulty=None):
        # Get a random simulation for this category
        simulation = self.get_random_simulation(request.user, category, difficulty)
        
        if not simulation:
            messages.error(request, f"No budget simulations available for {category}.")
            return redirect(f'learn_{category}')
        
        # Get all expenses for this simulation
        expenses = Expense.objects.filter(BudgetSimulation=simulation)
        
        context = {
            'simulation': simulation,
            'expenses': expenses,
            'monthly_income': simulation.monthly_income,
            'difficulty': simulation.get_difficulty_display(),
            'category': category,
            'category_display': simulation.get_category_display(),
        }
        
        return render(request, self.template_name, context)
    
    def post(self, request, category):
        # Check if this is an AJAX request or a form submission
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        simulation_id = request.POST.get('simulation_id')
        selected_expenses = json.loads(request.POST.get('selected_expenses', '[]'))
        
        simulation = get_object_or_404(BudgetSimulation, id=simulation_id)
        all_expenses = Expense.objects.filter(BudgetSimulation=simulation)
        
        # Map URL category to database category code
        category_mapping = {
            'budget': 'BUD',
            'investing': 'INV',
            'savings': 'SAV',
            'balance': 'BAL',
            'credit': 'CRD',
            'taxes': 'TAX',
        }
        db_category = category_mapping.get(category, 'BUD')
        
        # Calculate total expense and identify essential expenses
        total_selected = 0
        essential_expenses = []
        selected_expense_objects = []
        
        for expense_id in selected_expenses:
            expense = get_object_or_404(Expense, id=expense_id)
            selected_expense_objects.append(expense)
            total_selected += float(expense.amount)
            if expense.essential:
                essential_expenses.append(expense)
        
        # Check if all essential expenses are included
        all_essential_expenses = all_expenses.filter(essential=True)
        missing_essential = [e for e in all_essential_expenses if e.id not in selected_expenses]
        
        # Check if the budget is within limits
        is_within_budget = total_selected <= float(simulation.monthly_income)
        
        # Determine if the user's budget is successful
        is_successful = is_within_budget and not missing_essential
        
        # Generate feedback
        feedback = []
        detailed_feedback = {}
        
        # Check for missing essential expenses
        if missing_essential:
            for expense in missing_essential:
                feedback.append(f"{expense.name}: {expense.feedback}")
                if not detailed_feedback.get('missing_essential'):
                    detailed_feedback['missing_essential'] = []
                detailed_feedback['missing_essential'].append({
                    'id': expense.id,
                    'name': expense.name,
                    'amount': float(expense.amount),
                    'feedback': expense.feedback
                })
        
        # Check if over budget
        if not is_within_budget:
            feedback.append(f"Your selected expenses (${total_selected:.2f}) exceed your monthly income (${float(simulation.monthly_income):.2f}).")
            detailed_feedback['over_budget'] = {
                'total_selected': total_selected,
                'monthly_income': float(simulation.monthly_income),
                'difference': total_selected - float(simulation.monthly_income)
            }
            
            # Check for optional expenses that could be removed
            optional_expenses = [e for e in selected_expense_objects if not e.essential]
            if optional_expenses:
                optional_feedback = []
                for expense in optional_expenses:
                    optional_feedback.append({
                        'id': expense.id,
                        'name': expense.name,
                        'amount': float(expense.amount),
                        'feedback': expense.feedback
                    })
                detailed_feedback['optional_expenses'] = optional_feedback
        
        # If successful, record progress
        xp_earned = 0
        if is_successful:
            _, created = QuestionProgress.objects.get_or_create(
                user=request.user,
                question_id=simulation_id,
                question_type='BS',
                category=db_category
            )
            
            # Only add XP if this is the first time completing the simulation
            if created:
                xp_mapping = {
                    'B': 50,
                    'I': 100,
                    'A': 150,
                }
                xp = xp_mapping.get(simulation.difficulty, 0)
                xp_earned = xp
                
                # Update the user's XP based on category
                user = request.user
                xp_field_mapping = {
                    'BUD': 'budget_xp',
                    'INV': 'investing_xp',
                    'SAV': 'savings_xp',
                    'BAL': 'balance_sheet_xp',
                    'CRD': 'credit_xp',
                    'TAX': 'taxes_xp',
                }
                xp_field = xp_field_mapping.get(db_category)
                
                if xp_field:
                    current_xp = getattr(user, xp_field)
                    setattr(user, xp_field, current_xp + xp)
                    user.save(update_fields=[xp_field])
                
                feedback.append(f"Great job! You've earned {xp} {simulation.get_category_display()} XP.")
            else:
                feedback.append("Great job creating a balanced budget!")
        
        # Select a random feedback item if there are any
        random_feedback = None
        if feedback:
            random_feedback = random.choice(feedback)
        
        # Prepare data
        data = {
            'is_successful': is_successful,
            'random_feedback': random_feedback,
            'detailed_feedback': detailed_feedback,
            'feedback': feedback,
            'missing_essential': [{'id': e.id, 'name': e.name, 'amount': float(e.amount), 'feedback': e.feedback} 
                                for e in missing_essential],
            'total_selected': total_selected,
            'monthly_income': float(simulation.monthly_income),
            'budget_difference': float(simulation.monthly_income) - total_selected,
            'selected_expenses': [{'id': e.id, 'name': e.name, 'amount': float(e.amount), 'essential': e.essential, 'feedback': e.feedback} 
                                for e in selected_expense_objects],
            'category': category,
        }
        
        # If this is an AJAX request, return JSON
        if is_ajax:
            return JsonResponse(data)
        else:
            # For a regular form submission (after successful completion)
            # Render the result page with the successful budget
            
            # Prepare selected expenses for the result page
            selected_expenses_data = []
            for expense in selected_expense_objects:
                selected_expenses_data.append({
                    'name': expense.name,
                    'amount': float(expense.amount),
                    'essential': expense.essential
                })
            
            # Prepare context for the result page
            context = {
                'is_successful': is_successful,
                'selected_expenses': selected_expense_objects,
                'selected_expenses_json': json.dumps(selected_expenses_data),
                'total_selected': total_selected,
                'monthly_income': float(simulation.monthly_income),
                'budget_difference': float(simulation.monthly_income) - total_selected,
                'category': category,
                'category_display': simulation.get_category_display(),
                'difficulty': simulation.get_difficulty_display(),
                'xp_earned': xp_earned
            }
            
            return render(request, 'budgetq/result.html', context)