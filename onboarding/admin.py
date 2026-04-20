from django.contrib import admin
from django.utils import timezone
from .models import Invitation, InvitationStatus


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display  = ('email', 'role_proffered', 'organization', 'status', 'invited_by', 'expires_at', 'is_valid')
    list_filter   = ('status', 'role_proffered', 'organization')
    search_fields = ('email', 'organization__name', 'invited_by__email')
    readonly_fields = ('id', 'token', 'invite_url', 'accepted_at', 'accepted_by', 'created_at', 'updated_at')
    raw_id_fields = ('invited_by', 'accepted_by')

    fieldsets = (
        ('Invitation',   {'fields': ('organization', 'email', 'role_proffered', 'target_entity_id', 'message')}),
        ('Sender',       {'fields': ('invited_by',)}),
        ('Token & Link', {'fields': ('token', 'invite_url')}),
        ('Lifecycle',    {'fields': ('status', 'expires_at', 'accepted_at', 'accepted_by')}),
        ('Timestamps',   {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    actions = ['revoke_selected']

    @admin.action(description='Revoke selected invitations')
    def revoke_selected(self, request, queryset):
        updated = queryset.filter(status=InvitationStatus.PENDING).update(
            status=InvitationStatus.REVOKED
        )
        self.message_user(request, f"{updated} invitation(s) revoked.")

    def is_valid(self, obj):
        return obj.is_valid
    is_valid.boolean = True
    is_valid.short_description = 'Valid?'
