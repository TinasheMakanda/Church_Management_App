"""
organizations/models/hierarchy.py
----------------------------------
The three-tier geographic / administrative hierarchy below Organization:

    Organization
        └── Region          (managed by an Arch Bishop)
                └── Province        (managed by a Bishop)
                        └── Church          (managed by a Church Admin)

Each model carries:
  * organization FK  — enforces data isolation across tenants
  * leader FK        — FK to users.User (set via string ref to avoid circular imports)
  * payment_metadata — stub for the Finance module at the Church level
"""

from django.db import models
from django.conf import settings
from chms.base_models import BaseModel


class Region(BaseModel):
    """
    A national or continental region within an Organization.
    Typically led by an Arch Bishop.

    Example: 'Southern Africa Region', 'West Africa Region'
    """

    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='regions',
    )
    leader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='led_regions',
        help_text="The Arch Bishop responsible for this region.",
    )

    name        = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    is_active   = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Region'
        verbose_name_plural = 'Regions'
        ordering = ['organization', 'name']
        # A region name must be unique within its organization
        unique_together = [('organization', 'name')]

    def __str__(self) -> str:
        return f"{self.name} ({self.organization.name})"


class Province(BaseModel):
    """
    A provincial / state-level division within a Region.
    Typically led by a Bishop.

    Example: 'Gauteng Province', 'Cape Town Province'
    """

    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='provinces',
    )
    region = models.ForeignKey(
        Region,
        on_delete=models.CASCADE,
        related_name='provinces',
    )
    leader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='led_provinces',
        help_text="The Bishop responsible for this province.",
    )

    name        = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    is_active   = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Province'
        verbose_name_plural = 'Provinces'
        ordering = ['organization', 'region', 'name']
        unique_together = [('organization', 'name')]

    def __str__(self) -> str:
        return f"{self.name} — {self.region.name}"


class Church(BaseModel):
    """
    A local church congregation, the leaf of the hierarchy.
    Managed by a Church Admin / Pastor.

    Finance stubs
    -------------
    * payment_provider / payment_metadata — will be wired up by the Finance
      module to handle local giving, pledges, and tithes.
    """

    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='churches',
    )
    province = models.ForeignKey(
        Province,
        on_delete=models.CASCADE,
        related_name='churches',
    )
    leader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='led_churches',
        help_text="Primary Church Admin / Pastor.",
    )

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------
    name         = models.CharField(max_length=255)
    description  = models.TextField(blank=True, default='')
    logo         = models.ImageField(upload_to='churches/logos/', null=True, blank=True)
    website      = models.URLField(blank=True, default='')

    # ------------------------------------------------------------------
    # Contact / Location
    # ------------------------------------------------------------------
    email        = models.EmailField(blank=True, default='')
    phone_number = models.CharField(max_length=30, blank=True, default='')
    address      = models.TextField(blank=True, default='')
    city         = models.CharField(max_length=100, blank=True, default='')
    country      = models.CharField(max_length=100, blank=True, default='')

    # ------------------------------------------------------------------
    # Capacity & service times (extensible via JSON)
    # ------------------------------------------------------------------
    seating_capacity = models.PositiveIntegerField(default=0)
    service_times    = models.JSONField(
        default=list, blank=True,
        help_text="e.g. [{'day': 'Sunday', 'time': '09:00'}]"
    )

    is_active = models.BooleanField(default=True)

    # ------------------------------------------------------------------
    # Finance stub (Finance module populates these)
    # ------------------------------------------------------------------
    payment_provider = models.CharField(
        max_length=50, blank=True, default='',
        help_text="Local payment provider override, e.g. 'payfast'"
    )
    payment_metadata = models.JSONField(
        default=dict, blank=True,
        help_text="Church-level payment config; API secrets stored in vault"
    )

    class Meta:
        verbose_name = 'Church'
        verbose_name_plural = 'Churches'
        ordering = ['organization', 'province', 'name']
        unique_together = [('organization', 'name')]

    def __str__(self) -> str:
        return f"{self.name} — {self.province.name}"
