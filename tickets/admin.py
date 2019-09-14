from django.contrib import admin
from tickets.models import Ticket, Label, Comment

# Register your models here.


class CommentsAdmin(admin.TabularInline):
    model = Comment


class TicketAdmin(admin.ModelAdmin):
    model = Ticket
    inlines = (CommentsAdmin, )


class LabelAdmin(admin.ModelAdmin):
    model = Label


admin.site.register(Ticket, TicketAdmin)
admin.site.register(Label, LabelAdmin)
