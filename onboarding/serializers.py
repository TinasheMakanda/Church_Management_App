"""
onboarding/serializers.py
--------------------------
Serializers for the Invitation lifecycle.

SendInvitationSerializer   — for POST /api/onboarding/invitations/
AcceptInvitationSerializer — for POST /api/onboarding/accept/{token}/
InvitationSerializer       — read-only detail / list
"""

from django.utils import timezone
from rest_framework import serializers
from users.models.roles import Role, INVITER_ROLES, ROLE_SCOPE
from .models import Invitation, InvitationStatus


# ---------------------------------------------------------------------------
# Read-only representation
# ---------------------------------------------------------------------------

class InvitationSerializer(serializers.ModelSerializer):
    invited_by_name = serializers.CharField(source='invited_by.full_name', read_only=True, default='')
    is_valid        = serializers.BooleanField(read_only=True)
    invite_url      = serializers.CharField(read_only=True)

    class Meta:
        model  = Invitation
        fields = [
            'id', 'organization', 'email', 'role_proffered',
            'target_entity_id', 'invited_by', 'invited_by_name',
            'token', 'status', 'is_valid', 'invite_url',
            'expires_at', 'accepted_at', 'message',
            'created_at', 'updated_at',
        ]
        read_only_fields = fields  # all read-only on this serializer


# ---------------------------------------------------------------------------
# Create (send) an invitation
# ---------------------------------------------------------------------------

class SendInvitationSerializer(serializers.Serializer):
    email            = serializers.EmailField()
    role_proffered   = serializers.ChoiceField(choices=Role.choices)
    target_entity_id = serializers.UUIDField(required=False, allow_null=True)
    message          = serializers.CharField(required=False, allow_blank=True, default='')

    def validate(self, data):
        request      = self.context['request']
        inviter      = request.user
        role         = data['role_proffered']

        # 1. Inviter must be allowed to invite
        if inviter.role not in INVITER_ROLES:
            raise serializers.ValidationError(
                "Your role does not permit sending invitations."
            )

        # 2. Inviter cannot grant a role higher than their own
        from users.permissions import role_rank
        if role_rank(role) >= role_rank(inviter.role):
            raise serializers.ValidationError(
                "You cannot invite someone to a role equal to or above your own."
            )

        # 3. Roles that require a target entity must include target_entity_id
        scope = ROLE_SCOPE.get(role, 'church')
        if scope in ('region', 'province', 'church') and not data.get('target_entity_id'):
            raise serializers.ValidationError(
                f"target_entity_id is required for the '{role}' role."
            )

        # 4. Check for an existing pending / accepted invitation to same email+role
        existing = Invitation.objects.filter(
            organization=inviter.organization,
            email=data['email'],
            role_proffered=role,
            status=InvitationStatus.PENDING,
        ).exists()
        if existing:
            raise serializers.ValidationError(
                "A pending invitation for this email and role already exists."
            )

        return data

    def create(self, validated_data):
        request = self.context['request']
        return Invitation.objects.create(
            organization=request.user.organization,
            invited_by=request.user,
            **validated_data,
        )


# ---------------------------------------------------------------------------
# Accept an invitation (token-based registration)
# ---------------------------------------------------------------------------

class AcceptInvitationSerializer(serializers.Serializer):
    token      = serializers.UUIDField()
    first_name = serializers.CharField(max_length=150)
    last_name  = serializers.CharField(max_length=150)
    password   = serializers.CharField(min_length=8, write_only=True)
    phone_number = serializers.CharField(max_length=30, required=False, default='')

    def validate_token(self, value):
        try:
            invitation = Invitation.objects.select_related('organization').get(token=value)
        except Invitation.DoesNotExist:
            raise serializers.ValidationError("Invalid invitation token.")

        if not invitation.is_valid:
            raise serializers.ValidationError(
                f"This invitation is no longer valid (status: {invitation.get_status_display()})."
            )

        self.context['invitation'] = invitation
        return value

    def create(self, validated_data):
        from users.models import User
        invitation = self.context['invitation']

        user = User.objects.create_user(
            email        = invitation.email,
            password     = validated_data['password'],
            first_name   = validated_data['first_name'],
            last_name    = validated_data['last_name'],
            phone_number = validated_data.get('phone_number', ''),
            organization = invitation.organization,
            role         = invitation.role_proffered,
        )
        invitation.accept(user)
        return user
