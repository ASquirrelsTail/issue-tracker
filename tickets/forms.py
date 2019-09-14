from django import forms
from tickets.models import Ticket, Comment


# class LabelForm(forms.ModelForm):
#     class Meta:
#         model = Label


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'content']
        labels = {
            'title': ('Title'),
            'content': ('Ticket'),
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
