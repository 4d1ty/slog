from django.forms import ModelForm
from .models import WebGame

class WebGameForm(ModelForm):
    class Meta:
        model = WebGame
        fields = ['title', 'description', 'zip_file', 'url']