# Views Documentation

## Overview

The application uses class-based views organized into several functional categories:
- Core Views (Home and Dashboard)
- User Management Views
- Learning Category Views
- Multiple Choice Question Management Views
- Financial Planning Views

## Core Views

### Index View
```python
class Index(TemplateView):
    template_name = "home_dashboard.html"
```
Primary landing page view for the application.

### HomeView
```python
class HomeView(TemplateView):
    template_name = 'theme.html'
```
Displays market data and financial information dashboard. Includes stock ticker functionality.

### Learning View
```python
class learningview(LoginRequiredMixin, TemplateView):
    template_name = 'customizelearning.html'
```
Displays personalized learning dashboard with:
- Progress tracking across categories
- XP and level calculations
- Completion percentages
- Category-specific navigation

Key Features:
- XP calculation (10 XP per question)
- Level progression (20 XP per level)
- Maximum level cap at 30
- Progress visualization for each category

## User Management Views

### User Creation
```python
class UserCreateView(CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = 'account/create.html'
    success_url = reverse_lazy('user_detail')
```
Handles new user registration with custom user creation form.

### User Detail
```python
class UserDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = User
    template_name = 'account/detail.html'
    context_object_name = 'user'
```
Displays user profile information. Access restricted to:
- The user viewing their own profile
- Superusers

### User Update
```python
class UserUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = User
    form_class = CustomUserChangeForm
    template_name = 'account/edit.html'
```
Handles user profile updates. Similar access restrictions as UserDetailView.

### User List
```python
class UserListView(LoginRequiredMixin, SuperUserRequiredMixin, ListView):
    model = User
    template_name = 'account/list.html'
    context_object_name = 'users'
```
Administrative view for user management. Restricted to superusers only.

### User Delete
```python
class UserDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = User
    template_name = 'account/delete.html'
    success_url = reverse_lazy('user_list')
```
Handles user account deletion. Restricted to:
- The user deleting their own account
- Superusers

## Learning Category Views

All category views inherit from `LoginRequiredMixin, TemplateView` and follow a similar pattern:

### Budget View
```python
class BudgetView(LoginRequiredMixin, TemplateView):
    template_name = "categories/budget.html"
```

### Savings View
```python
class SavingsView(LoginRequiredMixin, TemplateView):
    template_name = "categories/savings.html"
```

### Investing View
```python
class InvestingView(LoginRequiredMixin, TemplateView):
    template_name = "categories/investing.html"
```

### Taxes View
```python
class TaxesView(LoginRequiredMixin, TemplateView):
    template_name = "categories/taxes.html"
```

### Credit View
```python
class CreditView(LoginRequiredMixin, TemplateView):
    template_name = "categories/credit.html"
```

### Balance Sheet View
```python
class BalanceSheetView(LoginRequiredMixin, TemplateView):
    template_name = "categories/balance_sheet.html"
```

Common Features Across Category Views:
- Question completion tracking
- Learning game type organization
- URL mapping for different game types
- Context data including:
  - Completed questions count
  - Available learning games
  - Navigation URLs

## Multiple Choice Management Views

### List View
```python
class MultipleChoiceListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = MultipleChoice
    template_name = 'multiple_choice/list.html'
    context_object_name = 'questions'
    ordering = ['category', 'difficulty']
```
Displays all multiple choice questions. Staff-only access.

### Detail View
```python
class MultipleChoiceDetailView(LoginRequiredMixin, StaffRequiredMixin, DetailView):
    model = MultipleChoice
    template_name = 'multiple_choice/detail.html'
    context_object_name = 'question'
```
Shows detailed information about a specific question.

### Create View
```python
class MultipleChoiceCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = MultipleChoice
    form_class = MultipleChoiceForm
    template_name = 'multiple_choice/form.html'
    success_url = reverse_lazy('multiple_choice_list')
```
Handles creation of new multiple choice questions, including:
- Question content
- Answer
- Distractors (via formset)
- Category and difficulty settings

### Update View
```python
class MultipleChoiceUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = MultipleChoice
    form_class = MultipleChoiceForm
    template_name = 'multiple_choice/form.html'
    success_url = reverse_lazy('multiple_choice_list')
```
Similar to create view but for editing existing questions.

### Delete View
```python
class MultipleChoiceDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = MultipleChoice
    template_name = 'multiple_choice/delete.html'
    success_url = reverse_lazy('multiple_choice_list')
    context_object_name = 'question'
```
Handles question deletion with confirmation.

## Financial Planning Views

### Savings Lesson
```python
def savings_lesson(request):
    modules = SavingModule.objects.all()
    return render(request, "savings_lesson.html", {"modules": modules})
```
Displays savings education modules.

### Savings Goal
```python
def savings_goal(request):
    if request.method == "POST":
        target = request.POST["target_amount"]
        date = request.POST["goal_date"]
        goal = SavingsGoal(user=request.user, target_amount=target, goal_date=date)
        goal.save()
    goals = SavingsGoal.objects.filter(user=request.user)
    return render(request, "savings_goal.html", {"goals": goals})
```
Handles savings goal creation and tracking.

### Budgeting Lesson
```python
def budgeting_lesson(request):
    categories = BudgetCategory.objects.all()
    expenses = Expense.objects.filter(user=request.user)
    return render(request, "budgeting_lesson.html", {
        "categories": categories, 
        "expenses": expenses
    })
```
Displays budgeting categories and user expenses.

### Add Expense
```python
def add_expense(request):
    if request.method == "POST":
        category = BudgetCategory.objects.get(id=request.POST["category_id"])
        amount = request.POST["amount"]
        expense = Expense(user=request.user, category=category, amount=amount)
        expense.save()
    return redirect("budgeting_lesson")
```
Handles expense tracking functionality.

## Custom Mixins

### SuperUserRequiredMixin
```python
class SuperUserRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser
```
Restricts view access to superusers only.

### StaffRequiredMixin
```python
class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff
```
Restricts view access to staff members only.

## Best Practices

1. Authentication:
   - Use `LoginRequiredMixin` for protected views
   - Implement proper permission checks
   - Use appropriate mixins for staff/superuser access

2. Form Handling:
   - Validate form data
   - Handle formsets properly
   - Provide success/error messages

3. Context Data:
   - Include all necessary data for templates
   - Filter querysets appropriately
   - Use proper context object names

4. URL Handling:
   - Use reverse_lazy for success_urls
   - Maintain consistent URL patterns
   - Handle redirects appropriately