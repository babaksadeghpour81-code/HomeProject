from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from .models import (
    ResidentialProperty, IndustrialProperty, LandProperty,
    GardenProperty, PropertyImage
)


class PropertyImageInline(GenericTabularInline):
    model = PropertyImage
    extra = 1


@admin.register(ResidentialProperty)
class ResidentialPropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'property_type', 'status', 'owner', 'area', 'price', 'created_at', 'is_active')
    list_filter = ('status', 'property_type', 'location_phase', 'is_active')
    search_fields = ('title', 'description', 'owner__username')
    inlines = [PropertyImageInline]


@admin.register(IndustrialProperty)
class IndustrialPropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'owner', 'usage', 'area', 'price', 'created_at')
    list_filter = ('status', 'is_active')
    inlines = [PropertyImageInline]


@admin.register(LandProperty)
class LandPropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'owner', 'usage', 'area', 'price', 'created_at')
    list_filter = ('status', 'is_active')
    inlines = [PropertyImageInline]


@admin.register(GardenProperty)
class GardenPropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'owner', 'area', 'price', 'created_at')
    list_filter = ('status', 'is_active')
    inlines = [PropertyImageInline]