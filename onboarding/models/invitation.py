"""
onboarding/models/invitation.py
---------------------------------
Invitation is the engine that builds the entire database organically.
No user can join CHMS without a valid, unexpired invitation token.

Invitation flow
---------------
1. SUPER_ADMIN creates an Org → invites APOSTLE
2. APOSTLE invites ARCH_BISHOPs (attaches them to a Region)
3. ARCH_BISHOP accepts → invites BISHOPs (attaches to a Province)
4. BISHOP accepts → registers Province churches → invites CHURCH_ADMINs
5. CHURCH_ADMIN accepts → creates Groups, invites PASTORs / MEMBERs

Security
--------
* Token: UUID4 — unguessable, single-use.
* status: tracks lifecycle (PENDING → ACCEPTED | EXPIRED | REVOKED).
* expires_at: set on creation (default 7 days, configurable per invite).
* accepted_at: stamped when the invitee completes registration.
* invited_by: FK to the User who sent the invite (audit trail).
"""

import uuid
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone

from chms.base_models import BaseModel
from users.models.roles import Role


class InvitationStatus(models.TextChoices):
    PENDING  = 'PENDING',  'Pending'
    ACCEPTED = 'ACCEPTED', 'Accepted'
    EXPIRED  = 'EXPIRED',  'Expired'
    REVOKED  = 'REVOKED',  'Revoked'


def _default_expiry():
    days = getattr(settings, 'INVITATION_EXPIRY_DAYS', 7)
    return timezone.now() + timedelta(days=days)


class Invitation(BaseModel):
    """
    A single-use, time-limited invitation to join CHMS at a specific
    tier (role + target entity).

    target_entity_id
    ----------------
    This is a generic integer/UUID field that points to the
    Region, Province, or Church the invitee will be attached to.
    We keep it generic (not a GenericForeignKey) for simplicity;
    the accepting view resolves it based on `role_proffered`.

    Role → expected target model:
        ARCH_BISHOP  → Region.id
        BISHOP       → Province.id
        CHURCH_ADMIN → Church.id
        PASTOR       → Church.id
        MEMBER       → Church.id
        APOSTLE      → None (org-wide)
    """

    # ------------------------------------------------------------------
    # Tenant
    # ------------------------------------------------------------------
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='invitations',
    )

    # ------------------------------------------------------------------
    # Who is invited & to what role
    # ------------------------------------------------------------------
    email = models.EmailField(
        help_text="The email address the invitation is sent to."
    )
    role_proffered = models.CharField(
        max_length=30,
        choices=Role.choices,
        help_text="The role the invitee will assume on acceptance."
    )

    # ------------------------------------------------------------------
    # Target entity (nullable for org-wide roles like APOSTLE)
    # ------------------------------------------------------------------
    target_entity_id = models.UUIDField(
        null=True, blank=True,
        help_text=(
            "UUID of the Region / Province / Church the invitee joins. "
            "Null for organization-wide roles (SUPER_ADMIN, APOSTLE)."
        )
    )

    # ------------------------------------------------------------------
    # Sender
    # ------------------------------------------------------------------
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='sent_invitations',
    )

    # ------------------------------------------------------------------
    # Token & lifecycle
    # ------------------------------------------------------------------
    token      = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    status     = models.CharField(
        max_length=20,
        choices=InvitationStatus.choices,
        default=InvitationStatus.PENDING,
        db_index=True,
    )
    expires_at   = models.DateTimeField(default=_default_expiry)
    accepted_at  = models.DateTimeField(null=True, blank=True)
    accepted_by  = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='accepted_invitations',
    )

    # Optional personal message from inviter
    message = models.TextField(blank=True, default='')

    class Meta:
        verbose_name        = 'Invitation'
        verbose_name_plural = 'Invitations'
        ordering            = ['-created_at']
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['email', 'status']),
            models.Index(fields=['organization', 'status']),
        ]

    # ------------------------------------------------------------------
    # Business logic helpers
    # ------------------------------------------------------------------

    @property
    def is_valid(self) -> bool:
        """True if the invitation can still be accepted."""
        return (
            self.status == InvitationStatus.PENDING
            and timezone.now() < self.expires_at
        )

    def accept(self, user) -> None:
        """Mark the invitation as accepted by `user`."""
        self.status      = InvitationStatus.ACCEPTED
        self.accepted_at = timezone.now()
        self.accepted_by = user
        self.save(update_fields=['status', 'accepted_at', 'accepted_by'])

    def revoke(self) -> None:
        self.status = InvitationStatus.REVOKED
        self.save(update_fields=['status'])

    def expire(self) -> None:
        self.status = InvitationStatus.EXPIRED
        self.save(update_fields=['status'])

    @property
    def invite_url(self) -> str:
        base = getattr(settings, 'FRONTEND_BASE_URL', '')
        return f"{base}/onboarding/accept/{self.token}/"

    def __str__(self) -> str:
        return (
            f"Invitation → {self.email} as {self.get_role_proffered_display()} "
            f"[{self.get_status_display()}]"
        )
