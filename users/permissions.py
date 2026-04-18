"""
users/permissions.py
---------------------
DRF Permission classes that enforce:
  1. Tenant isolation  — users can only see/modify data in their Organization.
  2. Role-based access — specific roles can perform specific actions.

Usage
-----
    from users.permissions import IsSameOrganization, IsAdminRole, HasMinimumRole

    class MyViewSet(viewsets.ModelViewSet):
        permission_classes = [IsAuthenticated, IsSameOrganization, IsAdminRole]
"""

from rest_framework.permissions import BasePermission
from .models.roles import Role, ADMIN_ROLES, INVITER_ROLES

# Ordered role hierarchy (index = seniority, higher index = more senior)
ROLE_HIERARCHY = [
    Role.MEMBER,
    Role.DEACON,
    Role.ELDER,
    Role.MINISTER,
    Role.PASTOR,
    Role.CHURCH_ADMIN,
    Role.BISHOP,
    Role.ARCH_BISHOP,
    Role.APOSTLE,
    Role.SUPER_ADMIN,
]

_ROLE_RANK = {role: idx for idx, role in enumerate(ROLE_HIERARCHY)}


def role_rank(role: str) -> int:
    return _ROLE_RANK.get(role, -1)


# ---------------------------------------------------------------------------
# Base permission: same organization
# ---------------------------------------------------------------------------

class IsSameOrganization(BasePermission):
    """
    Allows access only to users who belong to the same Organization as
    the object being accessed.

    The view's queryset must already be pre-filtered to the tenant; this
    class adds an object-level check as a safety net.
    """
    message = "You do not have permission to access resources outside your organization."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.organization_id)

    def has_object_permission(self, request, view, obj):
        obj_org = getattr(obj, 'organization_id', None)
        return obj_org == request.user.organization_id


# ---------------------------------------------------------------------------
# Role-based permissions
# ---------------------------------------------------------------------------

class IsAdminRole(BasePermission):
    """Allows access only to users whose role is in ADMIN_ROLES."""
    message = "You need an administrative role to perform this action."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in ADMIN_ROLES
        )


class CanInvite(BasePermission):
    """Allows access only to users who are permitted to send invitations."""
    message = "You do not have permission to send invitations."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in INVITER_ROLES
        )


class IsSuperAdmin(BasePermission):
    message = "Only Super Admins can perform this action."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == Role.SUPER_ADMIN
        )


class IsApostle(BasePermission):
    message = "Only Apostles or Super Admins can perform this action."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in {Role.SUPER_ADMIN, Role.APOSTLE}
        )


class IsArchBishopOrAbove(BasePermission):
    message = "Arch Bishop role or above required."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and role_rank(request.user.role) >= role_rank(Role.ARCH_BISHOP)
        )


class IsBishopOrAbove(BasePermission):
    message = "Bishop role or above required."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and role_rank(request.user.role) >= role_rank(Role.BISHOP)
        )


class IsChurchAdminOrAbove(BasePermission):
    message = "Church Admin role or above required."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and role_rank(request.user.role) >= role_rank(Role.CHURCH_ADMIN)
        )


class HasMinimumRole(BasePermission):
    """
    Parameterised permission — use as a factory.

    Example:
        permission_classes = [IsAuthenticated, HasMinimumRole.of(Role.ELDER)]
    """
    minimum_role: str = Role.MEMBER

    @classmethod
    def of(cls, role: str):
        """Return a new permission class requiring at least `role`."""
        return type(
            f'HasMinimumRole_{role}',
            (cls,),
            {'minimum_role': role, 'message': f"Minimum role required: {role}"}
        )

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and role_rank(request.user.role) >= role_rank(self.minimum_role)
        )
