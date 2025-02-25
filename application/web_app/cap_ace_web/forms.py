from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from .models import MultipleChoice, MultipleChoiceDistractor, QuestionProgress

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('username', css_class='form-group col-md-6 mb-0'),
                Column('email', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('password1', css_class='form-group col-md-6 mb-0'),
                Column('password2', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Create Account', css_class='btn btn-primary')
        )

class CustomUserChangeForm(UserChangeForm):
    password = None  # Remove password field from edit form
    
    class Meta:
        model = User
        fields = ('username', 'email')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('username', css_class='form-group col-md-6 mb-0'),
                Column('email', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Update Account', css_class='btn btn-primary')
        )

#Stock Data Form
class StockTickerForm(forms.Form):
    tickers = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter tickers (comma separated)', 'class': 'form-control'})
    )

class MultipleChoiceForm(forms.ModelForm):
    class Meta:
        model = MultipleChoice
        fields = ['category', 'question', 'answer', 'feedback', 'difficulty']
        widgets = {
            'feedback': forms.Textarea(attrs={'rows': 3}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure the category choices are properly set
        self.fields['category'].choices = MultipleChoice.CATEGORIES
        self.fields['category'].widget.attrs.update({'class': 'form-select'})

class MultipleChoiceDistractorForm(forms.ModelForm):
    class Meta:
        model = MultipleChoiceDistractor
        fields = ['distractor']
        widgets = {
            'distractor': forms.Textarea(attrs={'rows': 2}),
        }

MultipleChoiceDistractorFormSet = forms.inlineformset_factory(
    MultipleChoice, 
    MultipleChoiceDistractor,
    form=MultipleChoiceDistractorForm,
    extra=3,
    min_num=2,
    max_num=4,
    validate_min=True
)