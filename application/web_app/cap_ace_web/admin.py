from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import MultipleChoice, MultipleChoiceDistractor, BudgetSimulation, Expense
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet
from decimal import Decimal

User = get_user_model()

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = ['username', 'email', 'last_done', 'is_staff', 'is_active']
    list_filter = ['is_staff', 'is_active', 'last_done']
    fieldsets = UserAdmin.fieldsets + (
        ('Progress', {'fields': ('last_done', 'budget_xp', 'investing_xp', 'savings_xp', 'balance_sheet_xp', 'credit_xp', 'taxes_xp', )}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Optional Fields', {
            'classes': ('wide',),
            'fields': ('email', 'last_done', 'budget_xp', 'investing_xp', 'savings_xp', 'balance_sheet_xp', 'credit_xp', 'taxes_xp')}
        ),
    )
    search_fields = ['username', 'email']
    ordering = ['username']

class MultipleChoiceDistractorInline(admin.TabularInline):
    model = MultipleChoiceDistractor
    extra = 3
    min_num = 2
    max_num = 4

class MultipleChoiceAdmin(admin.ModelAdmin):
    list_display = ('question', 'category', 'difficulty')
    list_filter = ('category', 'difficulty')
    search_fields = ('question', 'answer', 'feedback')
    inlines = [MultipleChoiceDistractorInline]
    fieldsets = (
        (None, {
            'fields': ('category', 'difficulty')
        }),
        ('Question Details', {
            'fields': ('question', 'answer', 'feedback')
        }),
    )

class ExpenseInlineFormSet(BaseInlineFormSet):
    """
    Custom formset for Expense inline to validate that essential expenses don't exceed monthly income
    """
    def clean(self):
        super().clean()
        
        # Count the number of forms with deletion flag (to be deleted)
        forms_to_delete = 0
        for form in self.forms:
            if form.cleaned_data.get('DELETE', False):
                forms_to_delete += 1
                
        # If all forms are being deleted, no validation needed
        if forms_to_delete == len(self.forms):
            return
        
        total_essential = Decimal('0.00')
        monthly_income = self.instance.monthly_income if self.instance and hasattr(self.instance, 'monthly_income') else Decimal('0.00')
        
        # For new budget simulations, get the monthly income from the parent form
        if not monthly_income and self.parent_form and hasattr(self.parent_form, 'cleaned_data'):
            monthly_income = self.parent_form.cleaned_data.get('monthly_income', Decimal('0.00'))
            
        # Calculate total essential expenses from all forms
        for form in self.forms:
            if not form.is_valid() or form.cleaned_data.get('DELETE', False):
                continue  # Skip invalid forms or forms marked for deletion
                
            if form.cleaned_data.get('essential', False):
                total_essential += form.cleaned_data.get('amount', Decimal('0.00'))
                
        # Validate that essential expenses don't exceed monthly income
        if total_essential > monthly_income:
            raise ValidationError(
                f"The sum of essential expenses (${total_essential}) exceeds the monthly income (${monthly_income}). "
                f"Either increase the monthly income or reduce essential expenses."
            )

class ExpenseInline(admin.TabularInline):
    model = Expense
    extra = 3
    min_num = 1
    max_num = 10
    formset = ExpenseInlineFormSet
    
    # Show a helpful message about essential expenses
    classes = ('collapse',)
    verbose_name_plural = "Expenses (Essential expenses must not exceed monthly income)"

class BudgetSimulationAdmin(admin.ModelAdmin):
    list_display = ('question', 'monthly_income', 'essential_expenses_sum', 'difficulty')
    search_fields = ('question', 'monthly_income')
    list_filter = ('difficulty',)
    inlines = [ExpenseInline]
    fieldsets = (
        (None, {
            'fields': ('monthly_income', 'difficulty')
        }),
        ('Question Details', {
            'fields': ('question',)
        }),
    )
    
    def essential_expenses_sum(self, obj):
        """Calculate and display the sum of all essential expenses"""
        total = sum(expense.amount for expense in obj.expenses.filter(essential=True))
        return f"${total:.2f}"
    essential_expenses_sum.short_description = "Essential Expenses"
    
    def save_related(self, request, form, formsets, change):
        """
        After saving the related objects, validate that essential expenses don't exceed monthly income
        """
        super().save_related(request, form, formsets, change)
        
        # Get the updated instance
        obj = form.instance
        
        # Calculate sum of essential expenses
        essential_expenses_sum = sum(expense.amount for expense in obj.expenses.filter(essential=True))
        
        # Store the validation result for admin message
        if essential_expenses_sum > obj.monthly_income:
            self.message_user(
                request, 
                f"Warning: The sum of essential expenses (${essential_expenses_sum}) exceeds the monthly income (${obj.monthly_income}).",
                level='WARNING'
            )


admin.site.register(User, CustomUserAdmin)
admin.site.register(MultipleChoice, MultipleChoiceAdmin)
admin.site.register(BudgetSimulation, BudgetSimulationAdmin)