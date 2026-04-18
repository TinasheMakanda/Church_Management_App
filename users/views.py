"""
users/views.py
---------------
DRF ViewSets for User and UserProfile.

Every queryset is pre-filtered to request.user.organization to enforce
multi-tenant data isolation at the API layer.
"""

from rest_framework import viewsets, permissions
from .models import User, UserProfile
from .permissions import IsSameOrganization, IsAdminRole
from .serializers import UserSerializer, UserProfileSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    CRUD for Users scoped to the authenticated user's Organization.

    list   GET  /api/auth/users/
    create POST /api/auth/users/
    ...
    """
    serializer_class   = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsSameOrganization]

    def get_queryset(self):
        return (
            User.objects
            .filter(organization=self.request.user.organization)
            .select_related('organization', 'profile')
            .order_by('last_name', 'first_name')
        )

    def get_permissions(self):
        """Mutating operations require an admin role."""
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [permissions.IsAuthenticated(), IsAdminRole()]
        return super().get_permissions()


class UserProfileViewSet(viewsets.ModelViewSet):
    """CRUD for UserProfile, also scoped to the org."""
    serializer_class   = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsSameOrganization]

    def get_queryset(self):
        return (
            UserProfile.objects
            .filter(user__organization=self.request.user.organization)
            .select_related('user', 'assigned_church', 'assigned_province', 'assigned_region')
        )
