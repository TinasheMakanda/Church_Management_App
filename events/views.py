"""
events/views.py
----------------
EventViewSet — scoped to org, filterable by scope/status/date.

Scope-based permission matrix:
  INTERNATIONAL events → APOSTLE or above to create/edit
  PROVINCIAL events    → BISHOP or above
  LOCAL events         → CHURCH_ADMIN or above
"""

from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend

from users.permissions import (
    IsSameOrganization,
    IsChurchAdminOrAbove,
    IsBishopOrAbove,
    IsApostle,
)
from .models import Event, EventScope
from .serializers import EventSerializer, EventListSerializer


class EventViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsSameOrganization]
    filter_backends    = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields   = ['scope', 'status', 'province', 'church', 'is_online']
    search_fields      = ['title', 'venue_name', 'description']
    ordering_fields    = ['start_datetime', 'title', 'created_at']
    ordering           = ['-start_datetime']

    def get_serializer_class(self):
        if self.action == 'list':
            return EventListSerializer
        return EventSerializer

    def get_queryset(self):
        return (
            Event.objects
            .filter(organization=self.request.user.organization)
            .select_related('organization', 'province', 'church', 'created_by')
            .prefetch_related('organizer_groups')
        )

    def get_permissions(self):
        if self.action not in ('list', 'retrieve'):
            # Determine required permission based on scope in request data
            scope = self.request.data.get('scope', EventScope.LOCAL)
            if scope == EventScope.INTERNATIONAL:
                return [permissions.IsAuthenticated(), IsApostle()]
            elif scope == EventScope.PROVINCIAL:
                return [permissions.IsAuthenticated(), IsBishopOrAbove()]
            else:
                return [permissions.IsAuthenticated(), IsChurchAdminOrAbove()]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(
            organization=self.request.user.organization,
            created_by=self.request.user,
        )
