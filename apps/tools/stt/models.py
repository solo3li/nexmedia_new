from decimal import Decimal
from django.db import models
from django.conf import settings
from apps.core.models import BaseModel

class SttSetting(BaseModel):
    is_active = models.BooleanField(default=True, verbose_name="تفعيل الأداة / Is Active")
    is_maintenance_mode = models.BooleanField(default=False, verbose_name="وضع الصيانة / Maintenance Mode")
    is_coming_soon = models.BooleanField(default=False, verbose_name="قريباً / Coming Soon")
    max_audio_size_mb = models.IntegerField(default=25, verbose_name="أقصى حجم للملف بالميجابايت / Max Size MB")
    max_duration_seconds = models.IntegerField(default=300, verbose_name="أقصى مدة بالثواني / Max Duration Sec")
    max_concurrent_operations = models.IntegerField(default=10, verbose_name="أقصى عمليات متزامنة / Max Concurrency")
    allowed_wallet = models.CharField(
        max_length=20,
        choices=[('standard', 'Standard'), ('premium', 'Premium'), ('both', 'Both')],
        default='both',
        verbose_name="المحفظة / Allowed Wallet"
    )

    class Meta:
        verbose_name = "إعدادات تحويل الصوت إلى نص / STT Setting"
        verbose_name_plural = "إعدادات تحويل الصوت إلى نص / STT Settings"

    def __str__(self):
        return f"STT Setting (Active: {self.is_active})"

class SttModelPricing(BaseModel):
    model_name = models.CharField(max_length=100, default='whisper-large-v3', verbose_name="النموذج / Model")
    provider_name = models.CharField(max_length=100, default='Whisper', verbose_name="المزود / Provider")
    billing_type = models.CharField(
        max_length=50,
        choices=[('per_request', 'Per Request'), ('per_minute', 'Per Minute')],
        default='per_request',
        verbose_name="نوع الفوترة / Billing Type"
    )
    fixed_cost = models.DecimalField(max_digits=10, decimal_places=4, default=Decimal('0.5000'), verbose_name="التكلفة الثابتة / Fixed Cost")
    cost_per_minute = models.DecimalField(max_digits=10, decimal_places=4, default=Decimal('0.2000'), verbose_name="تكلفة الدقيقة / Cost Per Minute")
    allowed_wallet = models.CharField(
        max_length=20,
        choices=[('standard', 'Standard'), ('premium', 'Premium'), ('both', 'Both')],
        default='both',
        verbose_name="المحفظة / Allowed Wallet"
    )
    is_active = models.BooleanField(default=True, verbose_name="مفعل / Is Active")

    class Meta:
        verbose_name = "تسعير تحويل الصوت إلى نص / STT Pricing"
        verbose_name_plural = "أسعار تحويل الصوت إلى نص / STT Pricings"

    def __str__(self):
        return f"STT - {self.model_name} ({self.fixed_cost} credits)"

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

    class Meta:
        verbose_name = "سجل تفريغ صوتي / STT Record"
        verbose_name_plural = "سجلات التفريغ الصوتي / STT Records"

    def __str__(self):
        return f"STT #{self.id} by {self.user.username} ({self.status})"
