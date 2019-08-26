from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.db.models import Sum
import datetime

# Create your models here.


class Issue(models.Model):
    user = models.ForeignKey(User)
    title = models.CharField(max_length=100)
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(null=True, default=None)
    approved = models.DateTimeField(null=True, default=None)
    doing = models.DateTimeField(null=True, default=None)
    done = models.DateTimeField(null=True, default=None)
    views = models.IntegerField(default=0)

    class Meta:
        permissions = (('can_update_status', 'Update Issue status.'),
                       ('can_edit_all_issues', 'Edit any user\'s issue'),)

    def __str__(self):
        return '{0} - {1}'.format(self.id, self.title)

    def get_absolute_url(self):
        return reverse('issue', kwargs={'pk': self.pk})

    @property
    def votes(self):
        '''
        Returns the sum of votes on an issue.
        '''
        return self.vote_set.all().aggregate(Sum('count'))['count__sum']

    @property
    def comments(self):
        '''
        Returns comments and replies to an issue.
        '''
        comments = self.comment_set.filter(reply_to=None)  # Is this the best way to do this?
        for comment in comments:
            comment.replies = self.comment_set.filter(reply_to=comment)

        return comments

    @property
    def status(self):
        '''
        Returns the issue's status.
        '''
        return 'Done' if self.done else 'Doing' if self.doing else 'Approved' if self.approved else 'Awaiting Approval'

    def has_voted(self, user):
        '''
        Checks if a user has voted for the issue.
        '''
        return bool(self.vote_set.filter(user=user))

    def set_status(self, status):
        '''
        Sets the issue's status by setting it's date, and the date of any preceding statuses, if it isn't already set.
        '''
        options = ('approved', 'doing', 'done')
        if status in options and getattr(self, status) is None:
            for option in options[:options.index(status) + 1]:
                if getattr(self, option) is None:
                    setattr(self, option, datetime.datetime.now())
            self.save()
            return status
        else:
            return False


class Label(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class Vote(models.Model):
    user = models.ForeignKey(User)
    issue = models.ForeignKey(Issue)
    count = models.IntegerField(default=1)

    def __str__(self):
        return 'Vote for issue {0} by {1}'.format(self.issue.id, self.user)

    def get_absolute_url(self):
        return reverse('issue', kwargs={'pk': self.issue.pk})


class Comment(models.Model):
    issue = models.ForeignKey(Issue)
    user = models.ForeignKey(User)
    reply_to = models.ForeignKey('self', on_delete=models.CASCADE, null=True, default=None)
    created = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(null=True, default=None)
    content = models.TextField()

    class Meta:
        permissions = (('can_edit_all_comments', 'Edit any user\'s comments.'),)

    def __str__(self):
        return 'By {0} on issue {1} @ {2}'.format(self.user.username, self.issue.title, self.created)

    def get_absolute_url(self):
        return reverse('issue', kwargs={'pk': self.issue.pk}) + '#comment-{0}'.format(self.pk)
