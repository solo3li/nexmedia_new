from django.contrib import admin
from .models import TextToImageSetting, TextToImageModelPricing, TextToImageGeneration

@admin.register(TextToImageSetting)
class TextToImageSettingAdmin(admin.ModelAdmin):
    list_display = ('id', 'is_active', 'is_maintenance_mode', 'is_coming_soon', 'max_prompt_length', 'max_concurrent_operations', 'allowed_wallet')
    list_editable = ('is_active', 'is_maintenance_mode', 'is_coming_soon')

@admin.register(TextToImageModelPricing)
class TextToImageModelPricingAdmin(admin.ModelAdmin):
    list_display = ('model_name', 'provider_name', 'cost_per_image', 'allowed_wallet', 'is_active')
    list_editable = ('cost_per_image', 'allowed_wallet', 'is_active')

@admin.register(TextToImageGeneration)
class TextToImageGenerationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'aspect_ratio', 'status', 'standard_credits_used', 'created_at')
    list_filter = ('status', 'aspect_ratio')
    search_fields = ('user__username', 'prompt')
