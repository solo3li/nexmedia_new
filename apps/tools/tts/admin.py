from django.contrib import admin
from .models import TtsSetting, TtsModelPricing, TtsGeneration

@admin.register(TtsSetting)
class TtsSettingAdmin(admin.ModelAdmin):
    list_display = ('id', 'is_active', 'is_maintenance_mode', 'is_coming_soon', 'max_text_length', 'max_concurrent_operations', 'allowed_wallet', 'updated_at')
    list_editable = ('is_active', 'is_maintenance_mode', 'is_coming_soon', 'max_concurrent_operations')

@admin.register(TtsModelPricing)
class TtsModelPricingAdmin(admin.ModelAdmin):
    list_display = ('quality_level', 'model_name', 'provider_name', 'billing_type', 'fixed_cost', 'cost_per_char', 'allowed_wallet', 'is_active')
    list_editable = ('fixed_cost', 'cost_per_char', 'allowed_wallet', 'is_active')
    list_filter = ('is_active', 'quality_level', 'provider_name')

@admin.register(TtsGeneration)
class TtsGenerationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'voice_name', 'quality', 'status', 'standard_credits_used', 'created_at')
    list_filter = ('status', 'quality', 'language')
    search_fields = ('user__username', 'text', 'voice_name')
    readonly_fields = ('id', 'created_at', 'updated_at')
