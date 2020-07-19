from django import forms

from .models import Deed, Comment


class NewDeedForm(forms.ModelForm):
    class Meta:
        model = Deed
        fields = ['category', 'nature', 'title', 'situation', 'intensity', 'private']


class ReactionForm(forms.Form):
    reaction = forms.ChoiceField(choices=(('li', 'like'), ('ap', 'applause'), ('me', 'meh'), ('la', 'laugh'), ('cr', 'cries')))


class ReflectionForm(forms.ModelForm):
    class Meta:
        model = Deed
        fields = ['reflection']


class CommentForm(forms.Form):
    body = forms.Textarea()
