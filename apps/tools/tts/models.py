from decimal import Decimal
from django.db import models
from django.conf import settings
from apps.core.models import BaseModel

class TtsSetting(BaseModel):
    is_active = models.BooleanField(default=True, verbose_name="تفعيل الأداة / Is Active")
    is_maintenance_mode = models.BooleanField(default=False, verbose_name="وضع الصيانة / Maintenance Mode")
    is_coming_soon = models.BooleanField(default=False, verbose_name="قريباً / Coming Soon")
    max_text_length = models.IntegerField(default=5000, verbose_name="الحد الأقصى للحروف / Max Text Length")
    max_concurrent_operations = models.IntegerField(default=10, verbose_name="أقصى عمليات متزامنة / Max Concurrency")
    allowed_wallet = models.CharField(
        max_length=20,
        choices=[('standard', 'Standard'), ('premium', 'Premium'), ('both', 'Both (Standard First)')],
        default='both',
        verbose_name="المحفظة المسموحة / Allowed Wallet"
    )

    class Meta:
        verbose_name = "إعدادات تحويل النص إلى صوت / TTS Setting"
        verbose_name_plural = "إعدادات تحويل النص إلى صوت / TTS Settings"

    def __str__(self):
        return f"TTS Setting (Active: {self.is_active})"

class TtsModelPricing(BaseModel):
    quality_level = models.CharField(max_length=50, default='standard', verbose_name="مستوى الجودة / Quality")
    model_name = models.CharField(max_length=100, default='gemini-2.5-flash-preview-tts', verbose_name="اسم النموذج / Model")
    provider_name = models.CharField(max_length=100, default='Gemini', verbose_name="المزود / Provider")
    billing_type = models.CharField(
        max_length=50,
        choices=[('per_request', 'Per Request'), ('per_char', 'Per Character')],
        default='per_request',
        verbose_name="نوع الفوترة / Billing Type"
    )
    fixed_cost = models.DecimalField(max_digits=10, decimal_places=4, default=Decimal('0.1000'), verbose_name="التكلفة الثابتة / Fixed Cost")
    cost_per_char = models.DecimalField(max_digits=10, decimal_places=4, default=Decimal('0.0001'), verbose_name="تكلفة الحرف / Cost Per Char")
    allowed_wallet = models.CharField(
        max_length=20,
        choices=[('standard', 'Standard'), ('premium', 'Premium'), ('both', 'Both')],
        default='both',
        verbose_name="المحفظة / Allowed Wallet"
    )
    is_active = models.BooleanField(default=True, verbose_name="مفعل / Is Active")

    class Meta:
        verbose_name = "تسعير تحويل النص إلى صوت / TTS Pricing"
        verbose_name_plural = "أسعار تحويل النص إلى صوت / TTS Pricings"

    def __str__(self):
        return f"TTS - {self.quality_level} ({self.fixed_cost} credits)"

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

    class Meta:
        verbose_name = "سجل توليد صوتي / TTS Record"
        verbose_name_plural = "سجلات التوليد الصوتي / TTS Records"

    def __str__(self):
        return f"TTS by {self.user.username} - {self.voice_name} ({self.status})"
