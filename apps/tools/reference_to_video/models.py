from decimal import Decimal
from django.db import models
from django.conf import settings
from apps.core.models import BaseModel

class ReferenceToVideoGeneration(BaseModel):
    STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reference_to_video_generations')
    reference_media_url = models.CharField(max_length=500)
    prompt = models.TextField()
    model_name = models.CharField(max_length=50, default='seedance')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')
    result_url = models.CharField(max_length=500, blank=True, default='')
    standard_credits_used = models.DecimalField(max_digits=12, decimal_places=4, default=Decimal('0.0000'))
    premium_credits_used = models.DecimalField(max_digits=12, decimal_places=4, default=Decimal('0.0000'))
    error_message = models.TextField(blank=True, default='')

    def __str__(self):
        return f"R2V #{self.id} ({self.model_name}) - {self.status}"
