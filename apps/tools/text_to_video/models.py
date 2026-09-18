from decimal import Decimal
from django.db import models
from django.conf import settings
from apps.core.models import BaseModel

class TextToVideoGeneration(BaseModel):
    STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='text_to_video_generations')
    prompt = models.TextField()
    model_name = models.CharField(max_length=50, default='veo-3.1-fast')
    resolution = models.CharField(max_length=20, default='720p') # 480p, 720p, 1080p
    duration_seconds = models.IntegerField(default=5)
    aspect_ratio = models.CharField(max_length=20, default='16:9')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')
    result_url = models.CharField(max_length=500, blank=True, default='')
    standard_credits_used = models.DecimalField(max_digits=12, decimal_places=4, default=Decimal('0.0000'))
    premium_credits_used = models.DecimalField(max_digits=12, decimal_places=4, default=Decimal('0.0000'))
    error_message = models.TextField(blank=True, default='')

    def __str__(self):
        return f"T2V #{self.id} by {self.user.username} ({self.status})"
