from django.db import models
from django.conf import settings
from apps.core.models import BaseModel

class SupportTicket(BaseModel):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('closed', 'Closed'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tickets')
    subject = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')

    def __str__(self):
        return f"Ticket #{self.id} - {self.subject} ({self.status})"

class TicketMessage(BaseModel):
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    attachment_url = models.CharField(max_length=500, blank=True, default='')
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        return f"Message by {self.sender.username} on #{self.ticket.id}"
