from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Issue(models.Model):
    user = models.ForeignKey(User)
    title = models.CharField(max_length=100)
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    approved = models.DateTimeField(null=True, default=None)
    doing = models.DateTimeField(null=True, default=None)
    done = models.DateTimeField(null=True, default=None)
    views = models.IntegerField(default=0)

    def __str__(self):
        return '{0} - {1}'.format(self.id, self.title)


class Label(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name
