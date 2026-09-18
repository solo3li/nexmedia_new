from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from apps.accounts.models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'standard_credits', 'premium_credits', 'country', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'country')
    fieldsets = UserAdmin.fieldsets + (
        ('Wallets & Profile', {'fields': ('standard_credits', 'premium_credits', 'country', 'phone_number', 'is_verified', 'avatar_url')}),
    )
