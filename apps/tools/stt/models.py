from decimal import Decimal
from django.db import models
from django.conf import settings
from apps.core.models import BaseModel

class SttTranscription(BaseModel):
    STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='stt_transcriptions')
    audio_url = models.CharField(max_length=500)
    language = models.CharField(max_length=20, default='auto')
    translate = models.BooleanField(default=False)
    target_language = models.CharField(max_length=20, blank=True, default='en')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')
    result_text = models.TextField(blank=True, default='')
    standard_credits_used = models.DecimalField(max_digits=12, decimal_places=4, default=Decimal('0.0000'))
    premium_credits_used = models.DecimalField(max_digits=12, decimal_places=4, default=Decimal('0.0000'))
    error_message = models.TextField(blank=True, default='')

    def __str__(self):
        return f"STT #{self.id} by {self.user.username} ({self.status})"
