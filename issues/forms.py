from django import forms
from issues.models import Issue, Label, Comment


# class LabelForm(forms.ModelForm):
#     class Meta:
#         model = Label


# class IssueForm(forms.ModelForm):
#     class Meta:
#         model = Issue
#         fields = ['title', 'content']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        labels = {
            'content': ('Comment:'),
        }
