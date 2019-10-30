from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.db.models import Sum
from django.utils import timezone
from credits.models import Wallet


class Label(models.Model):
    name = models.CharField(max_length=30, unique=True)

    class Meta:
        permissions = (('can_create_edit_delete_labels', 'Create, edit and delete labels.'),)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return '{}?labels={}'.format(reverse('tickets-list'), self.id)


class Ticket(models.Model):
    TICKET_TYPE_CHOICES = (
        ('Bug', 'Bug Report'),
        ('Feature', 'Feature Request'),
    )

    user = models.ForeignKey(User)
    ticket_type = models.CharField(max_length=7, choices=TICKET_TYPE_CHOICES, default='Bug')
    title = models.CharField(max_length=100)
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(null=True, default=None)
    approved = models.DateTimeField(null=True, default=None)
    doing = models.DateTimeField(null=True, default=None)
    done = models.DateTimeField(null=True, default=None)
    image = models.ImageField(null=True, blank=True)
    labels = models.ManyToManyField(Label, blank=True)

    class Meta:
        permissions = (('can_update_status', 'Update Ticket status.'),
                       ('can_edit_all_tickets', 'Edit any user\'s ticket'),
                       ('can_view_all_stats', 'View stats for any ticket'),)
        ordering = ['-created']

    def __str__(self):
        return '{0} - {1} - {2}'.format(self.id, self.title, self.noun)

    def get_absolute_url(self):
        return reverse('ticket', kwargs={'pk': self.pk})

    @property
    def noun(self):
        for ticket_type, noun in self.TICKET_TYPE_CHOICES:
            if ticket_type == self.ticket_type:
                return noun
        else:
            return 'Ticket'

    @property
    def selected_labels(self):
        return self.labels.all()

    @property
    def no_views(self):
        return self.pageview_set.all().count()

    @property
    def no_votes(self):
        '''
        Returns the sum of votes on an ticket.
        '''
        return self.vote_set.all().aggregate(Sum('count'))['count__sum'] or 0

    @property
    def comments(self):
        '''
        Returns comments and replies to an ticket.
        '''
        return self.comment_set.filter(reply_to=None)

    @property
    def no_comments(self):
        '''
        Returns total number of comments and replies.
        '''
        return self.comment_set.all().count()

    @property
    def status(self):
        '''
        Returns the ticket's status.
        '''
        return 'done' if self.done else 'doing' if self.doing else 'approved' if self.approved else 'awaiting approval'

    def has_voted(self, user):
        '''
        Checks if a user has voted for the ticket.
        '''
        return user.is_authenticated and bool(self.vote_set.filter(user=user))

    def vote(self, user, credits=0):
        '''
        Adds a vote if the user is eligible to do so.
        '''
        if self.ticket_type == 'Bug':  # Users can vote once for Bugs
            if not self.has_voted(user):
                vote = Vote(user=user, ticket=self)
                vote.save()
                return {'success': True, 'message': 'Successfully voted for bug fix.'}
            else:
                return {'success': False, 'message': 'Already voted for bug fix.'}

        elif self.ticket_type == 'Feature':  # Users require credits to vote for Features
            try:
                transaction = user.wallet.debit(credits)
            except Wallet.DoesNotExist:
                transaction = False
            if transaction:
                vote = Vote(user=user, ticket=self, count=credits, transaction=transaction)
                vote.save()
                return {'success': True, 'message': 'Successfully voted for feature.'}
            else:
                return {'success': False, 'message': 'Insufficient credits to vote for feature.'}

    def set_status(self, status):
        '''
        Sets the ticket's status by setting it's date, and the date of any preceding statuses, if it isn't already set.
        '''
        options = ('approved', 'doing', 'done')
        if status in options and getattr(self, status) is None:
            for option in options[:options.index(status) + 1]:
                if getattr(self, option) is None:
                    setattr(self, option, timezone.now())
            self.save()
            return status
        else:
            return False


class Pageview(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return 'View of ticket {0} at {1}'.format(self.ticket.id, self.created)

    def get_absolute_url(self):
        return reverse('ticket', kwargs={'pk': self.ticket.pk})


class Vote(models.Model):
    user = models.ForeignKey(User)
    ticket = models.ForeignKey(Ticket)
    count = models.IntegerField(default=1)
    created = models.DateTimeField(auto_now_add=True)
    transaction = models.ForeignKey('credits.Debit', null=True, default=None)

    def __str__(self):
        return 'Vote for ticket {0} by {1}'.format(self.ticket.id, self.user)

    def get_absolute_url(self):
        return reverse('ticket', kwargs={'pk': self.ticket.pk})


class Comment(models.Model):
    ticket = models.ForeignKey(Ticket)
    user = models.ForeignKey(User)
    reply_to = models.ForeignKey('self', on_delete=models.CASCADE, null=True, default=None, related_name='reply_to_set')
    created = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(null=True, default=None)
    content = models.TextField()

    class Meta:
        permissions = (('can_edit_all_comments', 'Edit any user\'s comments.'),)

    def __str__(self):
        return 'By {0} on ticket {1} @ {2}'.format(self.user.username, self.ticket.id, self.created.strftime('%d/%m/%y %H:%M'))

    def get_absolute_url(self):
        url_fragment = '#comment-{0}' if self.reply_to is None else '#reply-{0}'
        return reverse('ticket', kwargs={'pk': self.ticket.pk}) + url_fragment.format(self.pk)

    @property
    def noun(self):
        return 'reply' if self.reply_to is not None else 'comment'

    @property
    def replies(self):
        return self.reply_to_set.all()

    @property
    def no_replies(self):
        return self.reply_to_set.count()
