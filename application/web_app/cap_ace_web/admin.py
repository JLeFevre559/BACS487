from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import MultipleChoice, MultipleChoiceDistractor, BudgetSimulation, Expense, FlashCard
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
    
    # Fieldsets for viewing a user
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Progress', {'fields': ('last_done', 'budget_xp', 'investing_xp', 'savings_xp', 
                                'balance_sheet_xp', 'credit_xp', 'taxes_xp')}),
    )
    
    # Fieldsets for adding a user - make most fields optional
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
        ('Personal info', {
            'classes': ('wide',),
            'fields': ('email', ),
        }),
        ('Permissions', {
            'classes': ('wide',),
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups'),
        }),
    )
    
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['username']
    
    # Make sure all custom fields have default values to simplify user creation
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser
        
        # Help text for non-superusers
        if not is_superuser:
            form.base_fields['is_superuser'].disabled = True
            form.base_fields['user_permissions'].disabled = True
            
        return form
    
    def save_model(self, request, obj, form, change):
        """
        Override save_model to ensure all fields have appropriate default values
        when creating a new user
        """
        if not change:  # Only when creating a new user
            # Set default values for XP fields if they're None
            if obj.budget_xp is None:
                obj.budget_xp = 0
            if obj.investing_xp is None:
                obj.investing_xp = 0
            if obj.savings_xp is None:
                obj.savings_xp = 0
            if obj.balance_sheet_xp is None:
                obj.balance_sheet_xp = 0
            if obj.credit_xp is None:
                obj.credit_xp = 0
            if obj.taxes_xp is None:
                obj.taxes_xp = 0
                
        super().save_model(request, obj, form, change)

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

class FlashCardAdmin(admin.ModelAdmin):
    list_display = ('question', 'category', 'difficulty')
    search_fields = ('question', 'answer', 'feedback')
    list_filter = ('category', 'difficulty')
    fieldsets = (
        (None, {
            'fields': ('question', 'answer', 'feedback', 'category', 'difficulty')
        }),
    )

admin.site.register(User, CustomUserAdmin)
admin.site.register(MultipleChoice, MultipleChoiceAdmin)
admin.site.register(BudgetSimulation, BudgetSimulationAdmin)
admin.site.register(FlashCard, FlashCardAdmin)