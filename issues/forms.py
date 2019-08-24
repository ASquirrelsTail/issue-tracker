from django import forms
from issues.models import Issue, Label


class LabelForm(forms.ModelForm):
    class Meta:
        model = Label


class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ['title', 'content']
