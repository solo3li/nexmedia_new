from decimal import Decimal
from django.db import models
from django.conf import settings
from apps.core.models import BaseModel

class LipSyncSetting(BaseModel):
    is_active = models.BooleanField(default=True, verbose_name="تفعيل الأداة / Is Active")
    is_maintenance_mode = models.BooleanField(default=False, verbose_name="وضع الصيانة / Maintenance Mode")
    is_coming_soon = models.BooleanField(default=False, verbose_name="قريباً / Coming Soon")
    max_video_size_mb = models.IntegerField(default=100, verbose_name="أقصى حجم فيديو MB / Max Video MB")
    max_audio_size_mb = models.IntegerField(default=25, verbose_name="أقصى حجم صوت MB / Max Audio MB")
    max_duration_seconds = models.IntegerField(default=120, verbose_name="أقصى مدة بالثواني / Max Duration Sec")
    max_concurrent_operations = models.IntegerField(default=10, verbose_name="أقصى عمليات متزامنة / Max Concurrency")
    allowed_wallet = models.CharField(
        max_length=20,
        choices=[('standard', 'Standard'), ('premium', 'Premium'), ('both', 'Both')],
        default='both',
        verbose_name="المحفظة / Allowed Wallet"
    )

    class Meta:
        verbose_name = "إعدادات مزامنة الشفاه / LipSync Setting"
        verbose_name_plural = "إعدادات مزامنة الشفاه / LipSync Settings"

    def __str__(self):
        return f"LipSync Setting (Active: {self.is_active})"

class LipSyncModelPricing(BaseModel):
    model_name = models.CharField(max_length=100, default='vidu-lipsync-std', verbose_name="النموذج / Model")
    provider_name = models.CharField(max_length=100, default='CrunAI', verbose_name="المزود / Provider")
    billing_type = models.CharField(
        max_length=50,
        choices=[('flat_rate', 'Flat Rate'), ('per_second', 'Per Second')],
        default='flat_rate',
        verbose_name="نوع الفوترة / Billing Type"
    )
    cost_per_generation = models.DecimalField(max_digits=10, decimal_places=4, default=Decimal('10.0000'), verbose_name="التكلفة الثابتة / Cost Per Gen")
    cost_per_second = models.DecimalField(max_digits=10, decimal_places=4, default=Decimal('0.5000'), verbose_name="تكلفة الثانية / Per Sec")
    allowed_wallet = models.CharField(
        max_length=20,
        choices=[('standard', 'Standard'), ('premium', 'Premium'), ('both', 'Both')],
        default='both',
        verbose_name="المحفظة / Allowed Wallet"
    )
    is_active = models.BooleanField(default=True, verbose_name="مفعل / Is Active")

    class Meta:
        verbose_name = "تسعير مزامنة الشفاه / LipSync Pricing"
        verbose_name_plural = "أسعار مزامنة الشفاه / LipSync Pricings"

    def __str__(self):
        return f"LipSync - {self.model_name} ({self.cost_per_generation} credits)"

class LipSyncGeneration(BaseModel):
    STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='lipsync_generations')
    input_video_url = models.CharField(max_length=500)
    input_audio_url = models.CharField(max_length=500)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')
    result_url = models.CharField(max_length=500, blank=True, default='')
    standard_credits_used = models.DecimalField(max_digits=12, decimal_places=4, default=Decimal('0.0000'))
    premium_credits_used = models.DecimalField(max_digits=12, decimal_places=4, default=Decimal('0.0000'))
    error_message = models.TextField(blank=True, default='')

    class Meta:
        verbose_name = "سجل مزامنة الشفاه / LipSync Record"
        verbose_name_plural = "سجلات مزامنة الشفاه / LipSync Records"

    def __str__(self):
        return f"LipSync #{self.id} - {self.status}"
