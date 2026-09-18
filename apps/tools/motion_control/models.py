from decimal import Decimal
from django.db import models
from django.conf import settings
from apps.core.models import BaseModel

class MotionControlGeneration(BaseModel):
    STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='motion_control_generations')
    input_image_url = models.CharField(max_length=500)
    input_motion_video_url = models.CharField(max_length=500)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')
    result_url = models.CharField(max_length=500, blank=True, default='')
    standard_credits_used = models.DecimalField(max_digits=12, decimal_places=4, default=Decimal('0.0000'))
    premium_credits_used = models.DecimalField(max_digits=12, decimal_places=4, default=Decimal('0.0000'))
    error_message = models.TextField(blank=True, default='')

    def __str__(self):
        return f"MotionControl #{self.id} - {self.status}"
