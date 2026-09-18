from django.contrib import admin
from .models import LipSyncSetting, LipSyncModelPricing, LipSyncGeneration

@admin.register(LipSyncSetting)
class LipSyncSettingAdmin(admin.ModelAdmin):
    list_display = ('id', 'is_active', 'is_maintenance_mode', 'is_coming_soon', 'max_video_size_mb', 'max_duration_seconds', 'max_concurrent_operations', 'allowed_wallet')
    list_editable = ('is_active', 'is_maintenance_mode', 'is_coming_soon')

@admin.register(LipSyncModelPricing)
class LipSyncModelPricingAdmin(admin.ModelAdmin):
    list_display = ('model_name', 'provider_name', 'billing_type', 'cost_per_generation', 'cost_per_second', 'allowed_wallet', 'is_active')
    list_editable = ('cost_per_generation', 'cost_per_second', 'allowed_wallet', 'is_active')

@admin.register(LipSyncGeneration)
class LipSyncGenerationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'standard_credits_used', 'created_at')
    list_filter = ('status',)
    search_fields = ('user__username',)
