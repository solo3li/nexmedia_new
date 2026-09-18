from django.contrib import admin
from apps.support.models import SupportTicket, TicketMessage

class TicketMessageInline(admin.TabularInline):
    model = TicketMessage
    extra = 1

@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'subject', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('user__username', 'subject')
    inlines = [TicketMessageInline]
