from decimal import Decimal
from django.db import models
from django.conf import settings
from apps.core.models import BaseModel

class AvatarVideoSetting(BaseModel):
    is_active = models.BooleanField(default=True, verbose_name="تفعيل الأداة / Is Active")
    is_maintenance_mode = models.BooleanField(default=False, verbose_name="وضع الصيانة / Maintenance Mode")
    is_coming_soon = models.BooleanField(default=False, verbose_name="قريباً / Coming Soon")
    max_text_length = models.IntegerField(default=2000, verbose_name="أقصى طول للنص / Max Text Length")
    max_duration_seconds = models.IntegerField(default=60, verbose_name="أقصى مدة بالثواني / Max Duration Sec")
    max_concurrent_operations = models.IntegerField(default=10, verbose_name="أقصى عمليات متزامنة / Max Concurrency")
    allowed_wallet = models.CharField(
        max_length=20,
        choices=[('standard', 'Standard'), ('premium', 'Premium'), ('both', 'Both')],
        default='both',
        verbose_name="المحفظة / Allowed Wallet"
    )

    class Meta:
        verbose_name = "إعدادات الأفاتار المتكلم / Avatar Setting"
        verbose_name_plural = "إعدادات الأفاتار المتكلم / Avatar Settings"

    def __str__(self):
        return f"Avatar Setting (Active: {self.is_active})"

class AvatarVideoModelPricing(BaseModel):
    model_name = models.CharField(max_length=100, default='kling-avatar', verbose_name="النموذج / Model")
    provider_name = models.CharField(max_length=100, default='KlingAI', verbose_name="المزود / Provider")
    cost_per_generation = models.DecimalField(max_digits=10, decimal_places=4, default=Decimal('15.0000'), verbose_name="التكلفة الثابتة / Cost Per Gen")
    cost_per_second = models.DecimalField(max_digits=10, decimal_places=4, default=Decimal('1.0000'), verbose_name="تكلفة الثانية / Per Sec")
    allowed_wallet = models.CharField(
        max_length=20,
        choices=[('standard', 'Standard'), ('premium', 'Premium'), ('both', 'Both')],
        default='both',
        verbose_name="المحفظة / Allowed Wallet"
    )
    is_active = models.BooleanField(default=True, verbose_name="مفعل / Is Active")

    class Meta:
        verbose_name = "تسعير الأفاتار المتكلم / Avatar Pricing"
        verbose_name_plural = "أسعار الأفاتار المتكلم / Avatar Pricings"

    def __str__(self):
        return f"Avatar - {self.model_name} ({self.cost_per_generation} credits)"

class AvatarVideoGeneration(BaseModel):
    STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='avatar_video_generations')
    avatar_image_url = models.CharField(max_length=500)
    audio_url = models.CharField(max_length=500, blank=True, default='')
    prompt = models.TextField(blank=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')
    result_url = models.CharField(max_length=500, blank=True, default='')
    standard_credits_used = models.DecimalField(max_digits=12, decimal_places=4, default=Decimal('0.0000'))
    premium_credits_used = models.DecimalField(max_digits=12, decimal_places=4, default=Decimal('0.0000'))
    error_message = models.TextField(blank=True, default='')

    class Meta:
        verbose_name = "سجل فيديو الأفاتار / Avatar Record"
        verbose_name_plural = "سجلات فيديو الأفاتار / Avatar Records"

    def __str__(self):
        return f"Avatar #{self.id} - {self.status}"
