import secrets
from decimal import Decimal
from django.db import models
from django.conf import settings
from apps.core.models import BaseModel

class AffiliateProfile(BaseModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='affiliate_profile')
    referral_code = models.CharField(max_length=20, unique=True, blank=True)
    is_active = models.BooleanField(default=True)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('20.00')) # 20%

    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = secrets.token_hex(4).upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} ({self.referral_code})"

class AffiliateReferral(BaseModel):
    referrer = models.ForeignKey(AffiliateProfile, on_delete=models.CASCADE, related_name='referrals')
    referred_user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='referred_by')

    def __str__(self):
        return f"{self.referrer.referral_code} -> {self.referred_user.username}"

class AffiliateCommission(BaseModel):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('available', 'Available'),
        ('paid', 'Paid'),
    ]
    referrer = models.ForeignKey(AffiliateProfile, on_delete=models.CASCADE, related_name='commissions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='USD')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    description = models.CharField(max_length=255, blank=True, default='')

    def __str__(self):
        return f"{self.referrer.user.username} - {self.amount} {self.currency} ({self.status})"

class AffiliatePayout(BaseModel):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('paid', 'Paid'),
        ('rejected', 'Rejected'),
    ]
    referrer = models.ForeignKey(AffiliateProfile, on_delete=models.CASCADE, related_name='payouts')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='USD')
    payout_method = models.CharField(max_length=50) # PayPal, Vodafone Cash, Bank Transfer
    account_details = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"{self.referrer.user.username} Payout: {self.amount} ({self.status})"
