"""
groups/views.py
----------------
ViewSets for ChurchGroup and GroupMembership.
Groups are scoped to the authenticated user's Organization and Church.
"""

from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend

from users.permissions import IsSameOrganization, IsChurchAdminOrAbove
from .models import ChurchGroup, GroupMembership
from .serializers import ChurchGroupSerializer, GroupMembershipSerializer


class ChurchGroupViewSet(viewsets.ModelViewSet):
    serializer_class   = ChurchGroupSerializer
    permission_classes = [permissions.IsAuthenticated, IsSameOrganization]
    filter_backends    = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields   = ['church', 'group_type', 'is_active']
    search_fields      = ['name', 'description']
    ordering_fields    = ['name', 'group_type', 'created_at']
    ordering           = ['name']

    def get_queryset(self):
        return (
            ChurchGroup.objects
            .filter(organization=self.request.user.organization)
            .select_related('organization', 'church', 'leader')
            .prefetch_related('members', 'events')
        )

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [permissions.IsAuthenticated(), IsChurchAdminOrAbove()]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)


class GroupMembershipViewSet(viewsets.ModelViewSet):
    serializer_class   = GroupMembershipSerializer
    permission_classes = [permissions.IsAuthenticated, IsSameOrganization]
    filter_backends    = [DjangoFilterBackend]
    filterset_fields   = ['group', 'is_co_leader']

    def get_queryset(self):
        return (
            GroupMembership.objects
            .filter(group__organization=self.request.user.organization)
            .select_related('group', 'user')
        )

    def get_permissions(self):
        if self.action in ('create', 'destroy'):
            return [permissions.IsAuthenticated(), IsChurchAdminOrAbove()]
        return super().get_permissions()
