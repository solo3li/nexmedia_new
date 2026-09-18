from decimal import Decimal
from django.db import models
from django.conf import settings
from apps.core.models import BaseModel

class MotionControlSetting(BaseModel):
    is_active = models.BooleanField(default=True, verbose_name="تفعيل الأداة / Is Active")
    is_maintenance_mode = models.BooleanField(default=False, verbose_name="وضع الصيانة / Maintenance Mode")
    is_coming_soon = models.BooleanField(default=False, verbose_name="قريباً / Coming Soon")
    max_video_size_mb = models.IntegerField(default=100, verbose_name="أقصى حجم فيديو MB / Max Video MB")
    max_image_size_mb = models.IntegerField(default=25, verbose_name="أقصى حجم صورة MB / Max Image MB")
    max_duration_seconds = models.IntegerField(default=30, verbose_name="أقصى مدة بالثواني / Max Duration Sec")
    max_concurrent_operations = models.IntegerField(default=10, verbose_name="أقصى عمليات متزامنة / Max Concurrency")
    allowed_wallet = models.CharField(
        max_length=20,
        choices=[('standard', 'Standard'), ('premium', 'Premium'), ('both', 'Both')],
        default='both',
        verbose_name="المحفظة / Allowed Wallet"
    )

    class Meta:
        verbose_name = "إعدادات التحكم بالحركة / Motion Setting"
        verbose_name_plural = "إعدادات التحكم بالحركة / Motion Settings"

    def __str__(self):
        return f"Motion Setting (Active: {self.is_active})"

class MotionControlModelPricing(BaseModel):
    model_name = models.CharField(max_length=100, default='kling-motion-control', verbose_name="النموذج / Model")
    provider_name = models.CharField(max_length=100, default='KlingAI', verbose_name="المزود / Provider")
    billing_type = models.CharField(
        max_length=50,
        choices=[('flat_rate', 'Flat Rate'), ('per_second', 'Per Second')],
        default='flat_rate',
        verbose_name="نوع الفوترة / Billing Type"
    )
    cost_per_generation = models.DecimalField(max_digits=10, decimal_places=4, default=Decimal('20.0000'), verbose_name="التكلفة الثابتة / Cost Per Gen")
    cost_per_second = models.DecimalField(max_digits=10, decimal_places=4, default=Decimal('2.0000'), verbose_name="تكلفة الثانية / Per Sec")
    allowed_wallet = models.CharField(
        max_length=20,
        choices=[('standard', 'Standard'), ('premium', 'Premium'), ('both', 'Both')],
        default='both',
        verbose_name="المحفظة / Allowed Wallet"
    )
    is_active = models.BooleanField(default=True, verbose_name="مفعل / Is Active")

    class Meta:
        verbose_name = "تسعير التحكم بالحركة / Motion Pricing"
        verbose_name_plural = "أسعار التحكم بالحركة / Motion Pricings"

    def __str__(self):
        return f"Motion - {self.model_name} ({self.cost_per_generation} credits)"

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

    class Meta:
        verbose_name = "سجل التحكم بالحركة / Motion Record"
        verbose_name_plural = "سجلات التحكم بالحركة / Motion Records"

    def __str__(self):
        return f"MotionControl #{self.id} - {self.status}"
