from django.contrib import admin
from apps.affiliate.models import AffiliateProfile, AffiliateReferral, AffiliateCommission, AffiliatePayout

@admin.register(AffiliateProfile)
class AffiliateProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'referral_code', 'commission_rate', 'is_active')
    search_fields = ('user__username', 'referral_code')

@admin.register(AffiliateReferral)
class AffiliateReferralAdmin(admin.ModelAdmin):
    list_display = ('referrer', 'referred_user', 'created_at')

@admin.register(AffiliateCommission)
class AffiliateCommissionAdmin(admin.ModelAdmin):
    list_display = ('referrer', 'amount', 'currency', 'status', 'created_at')
    list_filter = ('status', 'currency')

@admin.register(AffiliatePayout)
class AffiliatePayoutAdmin(admin.ModelAdmin):
    list_display = ('referrer', 'amount', 'payout_method', 'account_details', 'status', 'created_at')
    list_filter = ('status', 'payout_method')
