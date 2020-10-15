from django import forms
from django.forms import ModelForm
from .models import Post
from django.utils.translation import gettext, gettext_lazy as _


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('group', 'text',)
        labels = {'group':'Выберите группу', 'text':'Введите текст',}
        help_texts = {'group':'Из уже существующих', 'text':'Любой текст',}
