from decimal import Decimal
from django.db import models
from django.conf import settings
from apps.core.models import BaseModel

class TtsGeneration(BaseModel):
    STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tts_generations')
    text = models.TextField()
    voice_name = models.CharField(max_length=100)
    language = models.CharField(max_length=50, default='ar')
    style_instruction = models.CharField(max_length=255, blank=True, default='')
    quality = models.CharField(max_length=20, default='Standard')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')
    result_url = models.CharField(max_length=500, blank=True, default='')
    standard_credits_used = models.DecimalField(max_digits=12, decimal_places=4, default=Decimal('0.0000'))
    premium_credits_used = models.DecimalField(max_digits=12, decimal_places=4, default=Decimal('0.0000'))
    error_message = models.TextField(blank=True, default='')

    def __str__(self):
        return f"TTS by {self.user.username} - {self.voice_name} ({self.status})"
