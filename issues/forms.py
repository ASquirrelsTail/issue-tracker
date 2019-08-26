from django import forms
from issues.models import Issue, Comment


# class LabelForm(forms.ModelForm):
#     class Meta:
#         model = Label


class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ['title', 'content']
        labels = {
            'title': ('Title'),
            'content': ('Issue'),
        }
        help_texts = {
            'title': ('The name or a brief description of the issue.'),
            'content': ('Explain the issue, include any error codes and hardware details if relevant.'),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        labels = {
            'content': ('Comment'),
        }
