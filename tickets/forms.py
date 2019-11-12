from django import forms
from tickets.models import Ticket, Comment, Label


class LabelForm(forms.ModelForm):
    class Meta:
        model = Label
        fields = ['name']


class FilterForm(forms.Form):
    '''
    For for filtering ticket list view.
    '''
    ORDER_BY_CHOICES = (
        ('', 'Most Recent'),
        ('created', 'Oldest'),
        ('-vote_count', 'Most Votes'),
        ('-view_count', 'Most Viewed'),
        ('-comment_count', 'Most Comments'),
    )

    FILTER_BY_STATUS_CHOICES = (
        ('', 'All'),
        ('awaiting', 'Awaiting Approval'),
        ('approved', 'Approved'),
        ('doing', 'Doing'),
        ('done', 'Done'),
    )

    FILTER_BY_TYPE_CHOICES = (('', 'All'),) + Ticket.TICKET_TYPE_CHOICES

    order_by = forms.ChoiceField(choices=ORDER_BY_CHOICES, required=False)
    status = forms.ChoiceField(choices=FILTER_BY_STATUS_CHOICES, required=False)
    ticket_type = forms.ChoiceField(choices=FILTER_BY_TYPE_CHOICES, required=False)
    labels = forms.ModelMultipleChoiceField(queryset=Label.objects.all(), required=False)


class TicketForm(forms.ModelForm):
    '''
    Form for editing Tickets.
    '''
    class Meta:
        model = Ticket
        fields = ['title', 'ticket_type', 'content', 'image', 'labels']
        labels = {
            'title': ('Title'),
            'content': ('Description'),
            'image': ('Image Attachment'),
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
            'image': ('Attach an image to help illustrate the bug.'),
            'labels': ('Add labels to help others find your bug report.'),
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
            'image': ('Attach an image to help illustrate your idea.'),
            'labels': ('Add labels to help others find your feature request.'),
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
