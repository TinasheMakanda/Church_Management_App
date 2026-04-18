"""
organizations/models/organization.py
-------------------------------------
Organization is the root multi-tenant entity.
Every piece of data in CHMS belongs to an Organization.
"""

from django.db import models
from chms.base_models import BaseModel


class Organization(BaseModel):
    """
    Top-level tenant.  One Organization = one church network / denomination.

    Future-proof fields
    -------------------
    * payment_provider / payment_metadata  — reserved for the Finance module
      (pledges, tithes, giving campaigns).
    """

    class Status(models.TextChoices):
        ACTIVE   = 'ACTIVE',   'Active'
        SUSPENDED = 'SUSPENDED', 'Suspended'
        ARCHIVED = 'ARCHIVED', 'Archived'

    # ------------------------------------------------------------------
    # Core identity
    # ------------------------------------------------------------------
    name        = models.CharField(max_length=255, unique=True)
    slug        = models.SlugField(max_length=255, unique=True,
                                   help_text="URL-safe short identifier, e.g. 'rccg-south-africa'")
    logo        = models.ImageField(upload_to='organizations/logos/', null=True, blank=True)
    website     = models.URLField(blank=True, default='')
    description = models.TextField(blank=True, default='')

    # ------------------------------------------------------------------
    # Contact
    # ------------------------------------------------------------------
    email        = models.EmailField(blank=True, default='')
    phone_number = models.CharField(max_length=30, blank=True, default='')
    address      = models.TextField(blank=True, default='')
    country      = models.CharField(max_length=100, blank=True, default='')

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    status = models.CharField(max_length=20, choices=Status.choices,
                               default=Status.ACTIVE)

    # ------------------------------------------------------------------
    # Finance metadata (stub — populated by the Finance module)
    # ------------------------------------------------------------------
    payment_provider = models.CharField(
        max_length=50, blank=True, default='',
        help_text="e.g. 'stripe', 'payfast', 'paystack'"
    )
    payment_metadata = models.JSONField(
        default=dict, blank=True,
        help_text="Provider-specific config (API keys stored in vault, not here)"
    )

    class Meta:
        verbose_name = 'Organization'
        verbose_name_plural = 'Organizations'
        ordering = ['name']

    def __str__(self) -> str:
        return self.name
