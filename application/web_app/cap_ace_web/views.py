from django.views.generic import TemplateView, DetailView
from .models import MultipleChoice, MultipleChoiceDistractor

class Index(TemplateView):
    template_name = "index.html"

class LearningDetailView(TemplateView):
    template_name = 'learndash/detail.html'
    # model = Photo
    # context_object_name = 'photo'