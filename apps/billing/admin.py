from django.contrib import admin
from apps.billing.models import Plan, Subscription, Payment, WalletTransaction, ManualPaymentMethod
from apps.billing.services import WalletService

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'name_ar', 'price_usd', 'price_egp', 'standard_credits_grant', 'premium_credits_grant', 'is_free_trial', 'is_default_registration_plan', 'is_active')
    list_filter = ('is_active', 'is_free_trial', 'is_default_registration_plan')
    search_fields = ('name', 'name_ar')

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'status', 'start_date', 'end_date')
    list_filter = ('status', 'plan')
    search_fields = ('user__username', 'user__email')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'plan', 'amount', 'currency', 'method', 'status', 'created_at')
    list_filter = ('method', 'status', 'currency')
    search_fields = ('user__username', 'transaction_id')
    actions = ['approve_manual_payment']

    def approve_manual_payment(self, request, queryset):
        for payment in queryset.filter(status='pending'):
            if payment.plan:
                WalletService.assign_plan(str(payment.user.id), str(payment.plan.id), reset_to_zero=False)
            payment.status = 'completed'
            payment.save(update_fields=['status'])
        self.message_user(request, "Selected pending payments approved and plans assigned!")
    approve_manual_payment.short_description = "Approve payment and allocate plan credits"

@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'user', 'tool_name', 'wallet_type', 'amount', 'balance_after', 'description')
    list_filter = ('wallet_type', 'tool_name')
    search_fields = ('user__username', 'description')

@admin.register(ManualPaymentMethod)
class ManualPaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
