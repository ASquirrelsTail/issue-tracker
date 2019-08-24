from django.contrib import admin
from issues.models import Issue, Label

# Register your models here.


class IssueAdmin(admin.ModelAdmin):
    model = Issue


class LabelAdmin(admin.ModelAdmin):
    model = Label


admin.site.register(Issue, IssueAdmin)
admin.site.register(Label, LabelAdmin)
