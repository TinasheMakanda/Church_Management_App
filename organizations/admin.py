"""
organizations/admin.py
-----------------------
Django Admin for the organizations hierarchy.
"""

from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import Organization, Region, Province, Church


class RegionInline(TabularInline):
    model = Region
    extra = 0
    fields = ('name', 'leader', 'is_active')
    show_change_link = True


class ProvinceInline(TabularInline):
    model = Province
    extra = 0
    fields = ('name', 'leader', 'is_active')
    show_change_link = True


class ChurchInline(TabularInline):
    model = Church
    extra = 0
    fields = ('name', 'leader', 'city', 'is_active')
    show_change_link = True


@admin.register(Organization)
class OrganizationAdmin(ModelAdmin):
    inlines = [RegionInline]
    list_display  = ('name', 'slug', 'status', 'country', 'created_at')
    list_filter   = ('status', 'country')
    search_fields = ('name', 'slug', 'email')
    prepopulated_fields = {'slug': ('name',)}
    fieldsets = (
        ('Identity', {'fields': ('name', 'slug', 'logo', 'description', 'website')}),
        ('Contact',  {'fields': ('email', 'phone_number', 'address', 'country')}),
        ('Status',   {'fields': ('status',)}),
        ('Finance',  {'fields': ('payment_provider', 'payment_metadata'), 'classes': ('collapse',)}),
    )


@admin.register(Region)
class RegionAdmin(ModelAdmin):
    inlines = [ProvinceInline]
    list_display  = ('name', 'organization', 'leader', 'is_active', 'created_at')
    list_filter   = ('organization', 'is_active')
    search_fields = ('name', 'organization__name')
    raw_id_fields = ('leader',)


@admin.register(Province)
class ProvinceAdmin(ModelAdmin):
    inlines = [ChurchInline]
    list_display  = ('name', 'region', 'organization', 'leader', 'is_active')
    list_filter   = ('organization', 'region', 'is_active')
    search_fields = ('name', 'region__name', 'organization__name')
    raw_id_fields = ('leader',)


@admin.register(Church)
class ChurchAdmin(ModelAdmin):
    list_display  = ('name', 'province', 'city', 'leader', 'is_active', 'seating_capacity')
    list_filter   = ('organization', 'province__region', 'province', 'is_active')
    search_fields = ('name', 'city', 'email', 'province__name')
    raw_id_fields = ('leader',)
    fieldsets = (
        ('Identity',  {'fields': ('organization', 'province', 'leader', 'name', 'logo', 'description', 'website')}),
        ('Contact',   {'fields': ('email', 'phone_number', 'address', 'city', 'country')}),
        ('Details',   {'fields': ('seating_capacity', 'service_times', 'is_active')}),
        ('Finance',   {'fields': ('payment_provider', 'payment_metadata'), 'classes': ('collapse',)}),
    )
