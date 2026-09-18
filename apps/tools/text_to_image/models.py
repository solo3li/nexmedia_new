from decimal import Decimal
from django.db import models
from django.conf import settings
from apps.core.models import BaseModel

class TextToImageSetting(BaseModel):
    is_active = models.BooleanField(default=True, verbose_name="تفعيل الأداة / Is Active")
    is_maintenance_mode = models.BooleanField(default=False, verbose_name="وضع الصيانة / Maintenance Mode")
    is_coming_soon = models.BooleanField(default=False, verbose_name="قريباً / Coming Soon")
    max_prompt_length = models.IntegerField(default=2000, verbose_name="أقصى طول للوصف / Max Prompt Length")
    max_concurrent_operations = models.IntegerField(default=10, verbose_name="أقصى عمليات متزامنة / Max Concurrency")
    allowed_wallet = models.CharField(
        max_length=20,
        choices=[('standard', 'Standard'), ('premium', 'Premium'), ('both', 'Both')],
        default='both',
        verbose_name="المحفظة / Allowed Wallet"
    )

    class Meta:
        verbose_name = "إعدادات توليد الصور / T2I Setting"
        verbose_name_plural = "إعدادات توليد الصور / T2I Settings"

    def __str__(self):
        return f"T2I Setting (Active: {self.is_active})"

class TextToImageModelPricing(BaseModel):
    model_name = models.CharField(max_length=100, default='grok-imagine', verbose_name="النموذج / Model")
    provider_name = models.CharField(max_length=100, default='CrunAI', verbose_name="المزود / Provider")
    cost_per_image = models.DecimalField(max_digits=10, decimal_places=4, default=Decimal('2.0000'), verbose_name="تكلفة الصورة / Cost Per Image")
    allowed_wallet = models.CharField(
        max_length=20,
        choices=[('standard', 'Standard'), ('premium', 'Premium'), ('both', 'Both')],
        default='both',
        verbose_name="المحفظة / Allowed Wallet"
    )
    is_active = models.BooleanField(default=True, verbose_name="مفعل / Is Active")

    class Meta:
        verbose_name = "تسعير توليد الصور / T2I Pricing"
        verbose_name_plural = "أسعار توليد الصور / T2I Pricings"

    def __str__(self):
        return f"T2I - {self.model_name} ({self.cost_per_image} credits)"

class TextToImageGeneration(BaseModel):
    STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='text_to_image_generations')
    prompt = models.TextField()
    model_name = models.CharField(max_length=50, default='grok-imagine')
    aspect_ratio = models.CharField(max_length=20, default='1:1')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')
    result_url = models.CharField(max_length=500, blank=True, default='')
    standard_credits_used = models.DecimalField(max_digits=12, decimal_places=4, default=Decimal('0.0000'))
    premium_credits_used = models.DecimalField(max_digits=12, decimal_places=4, default=Decimal('0.0000'))
    error_message = models.TextField(blank=True, default='')

    class Meta:
        verbose_name = "سجل توليد صورة من نص / T2I Record"
        verbose_name_plural = "سجلات توليد الصور من نص / T2I Records"

    def __str__(self):
        return f"T2I #{self.id} - {self.status}"
