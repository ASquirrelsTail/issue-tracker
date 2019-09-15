from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.db.models import Sum
from django.utils import timezone

# Create your models here.


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

    class Meta:
        permissions = (('can_update_status', 'Update Ticket status.'),
                       ('can_edit_all_tickets', 'Edit any user\'s ticket'),)

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

    def vote(self, user, votes=1):
        '''
        Adds a vote if the user is eligible to do so.
        '''
        if not self.has_voted(user):
            vote = Vote(user=user, ticket=self)
            vote.save()
            return True
        else:
            return False

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


class Label(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


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
        return reverse('ticket', kwargs={'pk': self.ticket.pk}) + '#comment-{0}'.format(self.pk)

    @property
    def replies(self):
        return self.reply_to_set.all()

    @property
    def no_replies(self):
        return self.reply_to_set.count()
