from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm

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

admin.site.register(User, CustomUserAdmin)