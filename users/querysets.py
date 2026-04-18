"""
users/querysets.py
-------------------
Tenant-aware QuerySet and Manager mixins.

Usage in views / viewsets
--------------------------
    class MyViewSet(viewsets.ModelViewSet):
        def get_queryset(self):
            return MyModel.objects.for_organization(self.request.user.organization)

Or use TenantModelMixin on any model to gain `.tenant_objects` manager:

    class MyModel(BaseModel):
        organization = models.ForeignKey(Organization, ...)
        tenant_objects = TenantManager()

Then in views:
    MyModel.tenant_objects.for_organization(org)
"""

from django.db import models


class TenantQuerySet(models.QuerySet):
    """QuerySet that adds a `.for_organization(org)` filter shortcut."""

    def for_organization(self, organization):
        return self.filter(organization=organization)

    def active(self):
        """Filter to active records (models that have an is_active field)."""
        return self.filter(is_active=True)


class TenantManager(models.Manager):
    """Manager that returns a TenantQuerySet."""

    def get_queryset(self):
        return TenantQuerySet(self.model, using=self._db)

    def for_organization(self, organization):
        return self.get_queryset().for_organization(organization)
