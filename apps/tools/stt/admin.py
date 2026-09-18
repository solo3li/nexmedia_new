from django.contrib import admin
from .models import SttSetting, SttModelPricing, SttTranscription

@admin.register(SttSetting)
class SttSettingAdmin(admin.ModelAdmin):
    list_display = ('id', 'is_active', 'is_maintenance_mode', 'is_coming_soon', 'max_audio_size_mb', 'max_duration_seconds', 'max_concurrent_operations', 'allowed_wallet')
    list_editable = ('is_active', 'is_maintenance_mode', 'is_coming_soon')

@admin.register(SttModelPricing)
class SttModelPricingAdmin(admin.ModelAdmin):
    list_display = ('model_name', 'provider_name', 'billing_type', 'fixed_cost', 'cost_per_minute', 'allowed_wallet', 'is_active')
    list_editable = ('fixed_cost', 'cost_per_minute', 'allowed_wallet', 'is_active')

@admin.register(SttTranscription)
class SttTranscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'language', 'translate', 'status', 'standard_credits_used', 'created_at')
    list_filter = ('status', 'language', 'translate')
    search_fields = ('user__username', 'result_text')
