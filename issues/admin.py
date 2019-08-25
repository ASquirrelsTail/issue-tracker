from django.contrib import admin
from issues.models import Issue, Label, Comment

# Register your models here.


class CommentsAdmin(admin.TabularInline):
    model = Comment


class IssueAdmin(admin.ModelAdmin):
    model = Issue
    inlines = (CommentsAdmin, )


class LabelAdmin(admin.ModelAdmin):
    model = Label


admin.site.register(Issue, IssueAdmin)
admin.site.register(Label, LabelAdmin)
