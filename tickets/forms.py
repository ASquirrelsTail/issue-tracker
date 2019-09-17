from django import forms
from tickets.models import Ticket, Comment


# class LabelForm(forms.ModelForm):
#     class Meta:
#         model = Label


class TicketForm(forms.ModelForm):
    '''
    Form for editing Tickets.
    '''
    class Meta:
        model = Ticket
        fields = ['title', 'ticket_type', 'content']
        labels = {
            'title': ('Title'),
            'content': ('Description'),
        }
        widgets = {
            'ticket_type': forms.HiddenInput(),
        }


class BugForm(TicketForm):
    '''
    Form for submitting Bug Reports.
    '''
    ticket_type = forms.CharField(widget=forms.HiddenInput(), initial='Bug')

    class Meta(TicketForm.Meta):
        help_texts = {
            'title': ('The name or a brief description of the bug.'),
            'content': ('Explain the bug, include any error codes and hardware details if relevant.'),
        }


class FeatureForm(TicketForm):
    '''
    Form for submitting Feature Requests.
    '''
    ticket_type = forms.CharField(widget=forms.HiddenInput(), initial='Feature')

    class Meta(TicketForm.Meta):
        help_texts = {
            'title': ('The name or a brief description of your suggested feature.'),
            'content': ('Explain your idea for a new feature.'),
        }


class VoteForm(forms.Form):
    '''
    Form for submitting a vote with credits.
    '''
    credits = forms.IntegerField(min_value=1, initial=1)


class CommentForm(forms.ModelForm):
    '''
    Form for submitting comments and replies.
    '''
    class Meta:
        model = Comment
        fields = ['content']
        labels = {
            'content': ('Comment'),
        }
