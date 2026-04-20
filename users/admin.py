"""
users/admin.py
---------------
Django Admin configuration for the users app.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User, UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'
    fields = (
        'ministry_title', 'ordination_date',
        'assigned_church', 'assigned_province', 'assigned_region',
        'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relation',
    )


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)

    # What shows in the list view
    list_display = (
        'email', 'full_name', 'role', 'organization',
        'is_active', 'is_staff', 'created_at',
    )
    list_filter  = ('role', 'is_active', 'is_staff', 'organization')
    search_fields = ('email', 'first_name', 'last_name', 'phone_number')
    ordering = ('last_name', 'first_name')

    # Field layout in the detail view
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'phone_number', 'address', 'date_of_birth', 'profile_picture', 'bio')}),
        (_('Organization & Role'), {'fields': ('organization', 'role')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'organization', 'role', 'password1', 'password2'),
        }),
    )

    readonly_fields = ('last_login', 'date_joined')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display  = ('user', 'ministry_title', 'assigned_church', 'ordination_date')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'ministry_title')
    list_filter   = ('assigned_church__province__organization',)
    raw_id_fields = ('user', 'assigned_church', 'assigned_province', 'assigned_region')
