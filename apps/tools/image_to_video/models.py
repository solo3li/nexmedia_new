from decimal import Decimal
from django.db import models
from django.conf import settings
from apps.core.models import BaseModel

class ImageToVideoGeneration(BaseModel):
    STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='image_to_video_generations')
    input_image_url = models.CharField(max_length=500)
    prompt = models.TextField(blank=True, default='')
    model_name = models.CharField(max_length=50, default='veo-3.1-fast')
    resolution = models.CharField(max_length=20, default='720p')
    duration_seconds = models.IntegerField(default=5)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')
    result_url = models.CharField(max_length=500, blank=True, default='')
    standard_credits_used = models.DecimalField(max_digits=12, decimal_places=4, default=Decimal('0.0000'))
    premium_credits_used = models.DecimalField(max_digits=12, decimal_places=4, default=Decimal('0.0000'))
    error_message = models.TextField(blank=True, default='')

    def __str__(self):
        return f"I2V #{self.id} by {self.user.username} ({self.status})"
