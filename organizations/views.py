"""
organizations/views.py
-----------------------
DRF ViewSets for Organization, Region, Province, and Church.

Tenant isolation strategy
--------------------------
Every queryset is filtered by `request.user.organization`.
Super Admins still see only their own Organization's data through
normal views; a separate platform-admin interface (Django admin /
internal tooling) handles cross-tenant operations.

Role gating
-----------
  Organization  → SUPER_ADMIN / APOSTLE only (write)
  Region        → ARCH_BISHOP or above (write)
  Province      → BISHOP or above (write)
  Church        → CHURCH_ADMIN or above (write)
"""

from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend  # pip install django-filter

from users.permissions import (
    IsSameOrganization,
    IsAdminRole,
    IsApostle,
    IsArchBishopOrAbove,
    IsBishopOrAbove,
    IsChurchAdminOrAbove,
)
from .models import Organization, Region, Province, Church
from .serializers import (
    OrganizationSerializer,
    RegionSerializer,
    ProvinceSerializer,
    ChurchSerializer,
    ChurchListSerializer,
)


class OrganizationViewSet(viewsets.ModelViewSet):
    """
    Retrieve / update the authenticated user's Organization.
    Deletion is intentionally disabled — must go through a
    dedicated decommission workflow.
    """
    serializer_class   = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated, IsSameOrganization]
    http_method_names  = ['get', 'post', 'put', 'patch', 'head', 'options']  # no DELETE

    def get_queryset(self):
        return Organization.objects.filter(id=self.request.user.organization_id)

    def get_permissions(self):
        if self.action in ('update', 'partial_update'):
            return [permissions.IsAuthenticated(), IsApostle()]
        return super().get_permissions()


class RegionViewSet(viewsets.ModelViewSet):
    serializer_class   = RegionSerializer
    permission_classes = [permissions.IsAuthenticated, IsSameOrganization]
    filter_backends    = [filters.SearchFilter, filters.OrderingFilter]
    search_fields      = ['name']
    ordering_fields    = ['name', 'created_at']
    ordering           = ['name']

    def get_queryset(self):
        return (
            Region.objects
            .filter(organization=self.request.user.organization)
            .select_related('organization', 'leader')
        )

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [permissions.IsAuthenticated(), IsArchBishopOrAbove()]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)


class ProvinceViewSet(viewsets.ModelViewSet):
    serializer_class   = ProvinceSerializer
    permission_classes = [permissions.IsAuthenticated, IsSameOrganization]
    filter_backends    = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields   = ['region', 'is_active']
    search_fields      = ['name']
    ordering_fields    = ['name', 'created_at']
    ordering           = ['name']

    def get_queryset(self):
        return (
            Province.objects
            .filter(organization=self.request.user.organization)
            .select_related('organization', 'region', 'leader')
        )

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [permissions.IsAuthenticated(), IsBishopOrAbove()]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)


class ChurchViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsSameOrganization]
    filter_backends    = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields   = ['province', 'is_active', 'city']
    search_fields      = ['name', 'city', 'email']
    ordering_fields    = ['name', 'city', 'created_at']
    ordering           = ['name']

    def get_serializer_class(self):
        if self.action == 'list':
            return ChurchListSerializer
        return ChurchSerializer

    def get_queryset(self):
        return (
            Church.objects
            .filter(organization=self.request.user.organization)
            .select_related('organization', 'province', 'province__region', 'leader')
        )

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [permissions.IsAuthenticated(), IsChurchAdminOrAbove()]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)
