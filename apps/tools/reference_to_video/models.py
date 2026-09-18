from decimal import Decimal
from django.db import models
from django.conf import settings
from apps.core.models import BaseModel

class ReferenceToVideoSetting(BaseModel):
    is_active = models.BooleanField(default=True, verbose_name="تفعيل الأداة / Is Active")
    is_maintenance_mode = models.BooleanField(default=False, verbose_name="وضع الصيانة / Maintenance Mode")
    is_coming_soon = models.BooleanField(default=False, verbose_name="قريباً / Coming Soon")
    max_prompt_length = models.IntegerField(default=1000, verbose_name="أقصى طول للوصف / Max Prompt Length")
    max_duration_seconds = models.IntegerField(default=30, verbose_name="أقصى مدة بالثواني / Max Duration Sec")
    max_concurrent_operations = models.IntegerField(default=10, verbose_name="أقصى عمليات متزامنة / Max Concurrency")
    allowed_wallet = models.CharField(
        max_length=20,
        choices=[('standard', 'Standard'), ('premium', 'Premium'), ('both', 'Both')],
        default='both',
        verbose_name="المحفظة / Allowed Wallet"
    )

    class Meta:
        verbose_name = "إعدادات تحويل المرجع إلى فيديو / R2V Setting"
        verbose_name_plural = "إعدادات تحويل المرجع إلى فيديو / R2V Settings"

    def __str__(self):
        return f"R2V Setting (Active: {self.is_active})"

class ReferenceToVideoModelPricing(BaseModel):
    model_name = models.CharField(max_length=100, default='bytedance/seedance2-0-mini-r2v', verbose_name="النموذج / Model")
    provider_name = models.CharField(max_length=100, default='CrunAI', verbose_name="المزود / Provider")
    billing_type = models.CharField(
        max_length=50,
        choices=[('per_request', 'Per Request'), ('per_second', 'Per Second')],
        default='per_second',
        verbose_name="نوع الفوترة / Billing Type"
    )
    cost_per_second_720p = models.DecimalField(max_digits=10, decimal_places=4, default=Decimal('0.0286'), verbose_name="تكلفة الثانية 720p / Per Sec 720p")
    cost_per_second_1080p = models.DecimalField(max_digits=10, decimal_places=4, default=Decimal('0.0286'), verbose_name="تكلفة الثانية 1080p / Per Sec 1080p")
    fixed_cost = models.DecimalField(max_digits=10, decimal_places=4, default=Decimal('15.0000'), verbose_name="التكلفة الثابتة / Fixed Cost")
    allowed_wallet = models.CharField(
        max_length=20,
        choices=[('standard', 'Standard'), ('premium', 'Premium'), ('both', 'Both')],
        default='both',
        verbose_name="المحفظة / Allowed Wallet"
    )
    is_active = models.BooleanField(default=True, verbose_name="مفعل / Is Active")

    class Meta:
        verbose_name = "تسعير تحويل المرجع إلى فيديو / R2V Pricing"
        verbose_name_plural = "أسعار تحويل المرجع إلى فيديو / R2V Pricings"

    def __str__(self):
        return f"R2V - {self.model_name} ({self.fixed_cost} credits)"

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

    class Meta:
        verbose_name = "سجل تحويل مرجع إلى فيديو / R2V Record"
        verbose_name_plural = "سجلات تحويل مرجع إلى فيديو / R2V Records"

    def __str__(self):
        return f"R2V #{self.id} ({self.model_name}) - {self.status}"
