from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, License


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        'username', 'email', 'role', 'agency_name',
        'has_active_license_display', 'phone_number', 'is_active'
    )
    list_filter = ('role', 'is_active')
    search_fields = ('username', 'email', 'phone_number', 'agency_name')
    fieldsets = UserAdmin.fieldsets + (
        ('اطلاعات آژانس', {
            'fields': ('role', 'phone_number', 'agency_name', 'agency_address', 'agency_phone', 'agency_logo', 'national_card_image', 'business_license_image',)
        }),
    )
    readonly_fields = ('national_card_image', 'business_license_image')  # ✅ فقط خواندنی

    @admin.display(description='لایسنس فعال؟', boolean=True)
    def has_active_license_display(self, obj):
        return obj.has_active_license


@admin.register(License)
class LicenseAdmin(admin.ModelAdmin):
    list_display = ('agency', 'license_key', 'status', 'issued_at', 'expires_at', 'is_active', 'amount_paid')
    list_filter = ('status', 'is_active')
    search_fields = ('agency__username', 'agency__agency_name', 'license_key')
    readonly_fields = ('issued_at',)