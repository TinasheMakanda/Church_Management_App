"""
organizations/admin.py
-----------------------
Django Admin for the organizations hierarchy.
"""

from django.contrib import admin
from .models import Organization, Region, Province, Church


class RegionInline(admin.TabularInline):
    model = Region
    extra = 0
    fields = ('name', 'leader', 'is_active')
    show_change_link = True


class ProvinceInline(admin.TabularInline):
    model = Province
    extra = 0
    fields = ('name', 'leader', 'is_active')
    show_change_link = True


class ChurchInline(admin.TabularInline):
    model = Church
    extra = 0
    fields = ('name', 'leader', 'city', 'is_active')
    show_change_link = True


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    inlines = [RegionInline]
    list_display  = ('name', 'slug', 'status', 'country', 'created_at')
    list_filter   = ('status', 'country')
    search_fields = ('name', 'slug', 'email')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('id', 'created_at', 'updated_at')
    fieldsets = (
        ('Identity', {'fields': ('id', 'name', 'slug', 'logo', 'description', 'website')}),
        ('Contact',  {'fields': ('email', 'phone_number', 'address', 'country')}),
        ('Status',   {'fields': ('status',)}),
        ('Finance',  {'fields': ('payment_provider', 'payment_metadata'), 'classes': ('collapse',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    inlines = [ProvinceInline]
    list_display  = ('name', 'organization', 'leader', 'is_active', 'created_at')
    list_filter   = ('organization', 'is_active')
    search_fields = ('name', 'organization__name')
    raw_id_fields = ('leader',)
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    inlines = [ChurchInline]
    list_display  = ('name', 'region', 'organization', 'leader', 'is_active')
    list_filter   = ('organization', 'region', 'is_active')
    search_fields = ('name', 'region__name', 'organization__name')
    raw_id_fields = ('leader',)
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(Church)
class ChurchAdmin(admin.ModelAdmin):
    list_display  = ('name', 'province', 'city', 'leader', 'is_active', 'seating_capacity')
    list_filter   = ('organization', 'province__region', 'province', 'is_active')
    search_fields = ('name', 'city', 'email', 'province__name')
    raw_id_fields = ('leader',)
    readonly_fields = ('id', 'created_at', 'updated_at')
    fieldsets = (
        ('Identity',  {'fields': ('id', 'organization', 'province', 'leader', 'name', 'logo', 'description', 'website')}),
        ('Contact',   {'fields': ('email', 'phone_number', 'address', 'city', 'country')}),
        ('Details',   {'fields': ('seating_capacity', 'service_times', 'is_active')}),
        ('Finance',   {'fields': ('payment_provider', 'payment_metadata'), 'classes': ('collapse',)}),
        ('Timestamps',{'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
