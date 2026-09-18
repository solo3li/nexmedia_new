from django.contrib import admin
from .models import TextToVideoSetting, TextToVideoModelPricing, TextToVideoGeneration

@admin.register(TextToVideoSetting)
class TextToVideoSettingAdmin(admin.ModelAdmin):
    list_display = ('id', 'is_active', 'is_maintenance_mode', 'is_coming_soon', 'default_resolution', 'max_duration_seconds', 'max_concurrent_operations', 'allowed_wallet')
    list_editable = ('is_active', 'is_maintenance_mode', 'is_coming_soon')

@admin.register(TextToVideoModelPricing)
class TextToVideoModelPricingAdmin(admin.ModelAdmin):
    list_display = ('model_name', 'provider_name', 'billing_type', 'fixed_cost_720p', 'fixed_cost_1080p', 'fixed_cost_4k', 'allowed_wallet', 'is_active')
    list_editable = ('fixed_cost_720p', 'fixed_cost_1080p', 'fixed_cost_4k', 'allowed_wallet', 'is_active')

@admin.register(TextToVideoGeneration)
class TextToVideoGenerationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'model_name', 'resolution', 'duration_seconds', 'status', 'standard_credits_used', 'created_at')
    list_filter = ('status', 'resolution', 'model_name')
    search_fields = ('user__username', 'prompt')
