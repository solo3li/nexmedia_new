from django.contrib import admin
from .models import AvatarVideoSetting, AvatarVideoModelPricing, AvatarVideoGeneration

@admin.register(AvatarVideoSetting)
class AvatarVideoSettingAdmin(admin.ModelAdmin):
    list_display = ('id', 'is_active', 'is_maintenance_mode', 'is_coming_soon', 'max_text_length', 'max_duration_seconds', 'max_concurrent_operations', 'allowed_wallet')
    list_editable = ('is_active', 'is_maintenance_mode', 'is_coming_soon')

@admin.register(AvatarVideoModelPricing)
class AvatarVideoModelPricingAdmin(admin.ModelAdmin):
    list_display = ('model_name', 'provider_name', 'cost_per_generation', 'cost_per_second', 'allowed_wallet', 'is_active')
    list_editable = ('cost_per_generation', 'cost_per_second', 'allowed_wallet', 'is_active')

@admin.register(AvatarVideoGeneration)
class AvatarVideoGenerationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'standard_credits_used', 'created_at')
    list_filter = ('status',)
    search_fields = ('user__username', 'prompt')
