import uuid
from decimal import Decimal
from django.db import models
from django.conf import settings
from apps.core.models import BaseModel

class Plan(BaseModel):
    name = models.CharField(max_length=100)
    name_ar = models.CharField(max_length=100)
    description = models.TextField(blank=True, default="")
    description_ar = models.TextField(blank=True, default="")
    price_usd = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    price_egp = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    duration_days = models.IntegerField(default=30)
    grace_period_days = models.IntegerField(default=3)

    standard_credits_grant = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal('100.0000'))
    premium_credits_grant = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal('0.0000'))

    is_free_trial = models.BooleanField(default=False)
    is_default_registration_plan = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    # Tool access flags (9 tools)
    tts_enabled = models.BooleanField(default=True)
    stt_enabled = models.BooleanField(default=True)
    text_to_video_enabled = models.BooleanField(default=True)
    image_to_video_enabled = models.BooleanField(default=True)
    reference_to_video_enabled = models.BooleanField(default=True)
    lipsync_enabled = models.BooleanField(default=True)
    motion_control_enabled = models.BooleanField(default=True)
    text_to_image_enabled = models.BooleanField(default=True)
    avatar_video_enabled = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} (${self.price_usd})"

class Subscription(BaseModel):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('freeze', 'Freeze'),
        ('expired', 'Expired'),
        ('canceled', 'Canceled'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name='subscriptions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    def __str__(self):
        return f"{self.user.username} - {self.plan.name} ({self.status})"

class Payment(BaseModel):
    METHOD_CHOICES = [
        ('paymob', 'Paymob (EGP)'),
        ('paypal', 'PayPal (USD)'),
        ('manual', 'Manual Bank/Wallet'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='USD')
    method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=255, blank=True, null=True)
    receipt_url = models.CharField(max_length=500, blank=True, null=True)
    admin_notes = models.TextField(blank=True, default="")

    def __str__(self):
        return f"Payment {self.id} - {self.amount} {self.currency} ({self.status})"

class WalletTransaction(BaseModel):
    WALLET_CHOICES = [
        ('standard', 'Standard Credits'),
        ('premium', 'Premium Credits'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wallet_transactions')
    tool_name = models.CharField(max_length=50, blank=True, default="")
    wallet_type = models.CharField(max_length=20, choices=WALLET_CHOICES)
    amount = models.DecimalField(max_digits=14, decimal_places=4) # Negative for debit, positive for credit/refund
    balance_after = models.DecimalField(max_digits=14, decimal_places=4)
    description = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.user.username} - {self.amount} {self.wallet_type} ({self.tool_name})"

class ManualPaymentMethod(BaseModel):
    name = models.CharField(max_length=100)
    account_details = models.TextField(help_text="Account number, IBAN, Vodafone Cash number, etc.")
    instructions = models.TextField(blank=True, default="")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
