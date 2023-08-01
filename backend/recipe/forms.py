from django.forms import ModelForm
from django.forms.widgets import TextInput
from recipe.models import Tag


class TagForm(ModelForm):
    class Meta:
        model = Tag
        fields = '__all__'
        widgets = {
            'color': TextInput(attrs={'type': 'color'}),
        }
