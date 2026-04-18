"""
users/models/user.py
---------------------
Custom User model for CHMS.

Inherits from AbstractUser so we keep Django's auth infrastructure
(groups, permissions, password hashing, session framework) while
adding:
  * UUID primary key (via BaseModel)
  * organization FK  — multi-tenancy anchor
  * role            — single canonical role within the org
  * phone_number / address — ministry contact details
  * profile_picture / bio   — public-facing profile

Design decisions
----------------
* We keep AbstractUser's username field (required by Django admin).
  Login is by email; username is auto-populated from email prefix.
* The `organization` FK is nullable so a freshly-created SUPER_ADMIN
  account can exist before any Organization is set up.
* `role` defaults to MEMBER — the safest / lowest-privilege value.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from chms.base_models import UUIDModel, TimeStampedModel
from users.managers import UserManager
from .roles import Role


class User(UUIDModel, TimeStampedModel, AbstractUser):
    """
    The single User model for all CHMS users regardless of role.

    Multi-tenancy note
    ------------------
    `organization` is the tenant key.  All queryset filtering in views
    and serializers MUST include `.filter(organization=request.user.organization)`.
    The `TenantQuerySet` mixin (users/querysets.py) centralises this.
    """

    # ------------------------------------------------------------------
    # Tenant binding
    # ------------------------------------------------------------------
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='users',
        null=True,   # null during initial SUPER_ADMIN bootstrap
        blank=True,
        help_text=_("The Organization this user belongs to.")
    )

    # ------------------------------------------------------------------
    # Role
    # ------------------------------------------------------------------
    role = models.CharField(
        max_length=30,
        choices=Role.choices,
        default=Role.MEMBER,
        db_index=True,
        help_text=_("The user's primary role within their Organization.")
    )

    # ------------------------------------------------------------------
    # Contact
    # ------------------------------------------------------------------
    email = models.EmailField(
        _('email address'),
        unique=True,
        help_text=_("Used as the primary login identifier.")
    )
    phone_number = models.CharField(
        max_length=30,
        blank=True,
        default='',
        help_text=_("International format recommended, e.g. +27 82 000 0000")
    )
    address = models.TextField(
        blank=True,
        default='',
        help_text=_("Residential or postal address.")
    )

    # ------------------------------------------------------------------
    # Profile
    # ------------------------------------------------------------------
    profile_picture = models.ImageField(
        upload_to='users/profile_pictures/',
        null=True,
        blank=True,
    )
    bio = models.TextField(
        blank=True,
        default='',
        help_text=_("Short ministry biography, displayed on public profiles.")
    )
    date_of_birth = models.DateField(null=True, blank=True)

    # ------------------------------------------------------------------
    # Manager
    # ------------------------------------------------------------------
    objects = UserManager()

    # ------------------------------------------------------------------
    # Django auth wiring
    # ------------------------------------------------------------------
    # Login by email, not username
    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name        = _('User')
        verbose_name_plural = _('Users')
        ordering            = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['organization', 'role']),
            models.Index(fields=['organization', 'email']),
        ]

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip() or self.email

    @property
    def is_admin_role(self) -> bool:
        from .roles import ADMIN_ROLES
        return self.role in ADMIN_ROLES

    @property
    def can_invite(self) -> bool:
        from .roles import INVITER_ROLES
        return self.role in INVITER_ROLES

    def __str__(self) -> str:
        return f"{self.full_name} <{self.email}> [{self.get_role_display()}]"
