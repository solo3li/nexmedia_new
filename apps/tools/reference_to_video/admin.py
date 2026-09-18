from django.contrib import admin
from .models import ReferenceToVideoSetting, ReferenceToVideoModelPricing, ReferenceToVideoGeneration

@admin.register(ReferenceToVideoSetting)
class ReferenceToVideoSettingAdmin(admin.ModelAdmin):
    list_display = ('id', 'is_active', 'is_maintenance_mode', 'is_coming_soon', 'max_duration_seconds', 'max_concurrent_operations', 'allowed_wallet')
    list_editable = ('is_active', 'is_maintenance_mode', 'is_coming_soon')

@admin.register(ReferenceToVideoModelPricing)
class ReferenceToVideoModelPricingAdmin(admin.ModelAdmin):
    list_display = ('model_name', 'provider_name', 'billing_type', 'fixed_cost', 'cost_per_second_720p', 'allowed_wallet', 'is_active')
    list_editable = ('fixed_cost', 'cost_per_second_720p', 'allowed_wallet', 'is_active')

@admin.register(ReferenceToVideoGeneration)
class ReferenceToVideoGenerationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'model_name', 'status', 'standard_credits_used', 'created_at')
    list_filter = ('status', 'model_name')
    search_fields = ('user__username', 'prompt')
