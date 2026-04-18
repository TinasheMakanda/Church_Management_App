"""
events/models/event.py
-----------------------
Event is scoped to one of three levels:

    INTERNATIONAL  → belongs to the whole Organization
    PROVINCIAL     → scoped to a Province
    LOCAL          → scoped to a Church

The nullable FKs (province, church) encode the scope:
  - INTERNATIONAL:  province=None, church=None
  - PROVINCIAL:     province=<obj>, church=None
  - LOCAL:          province=<obj>, church=<obj>

Organizer groups
----------------
The inverse of ChurchGroup.events M2M gives us
`event.organizer_groups.all()` — a queryset of Taskforces/Groups
responsible for running this event.

Finance hook
------------
`budget` and `finance_metadata` are stubs for the Finance module
to track event-level revenue targets and expenses.
"""

from django.conf import settings
from django.db import models
from chms.base_models import BaseModel


class EventScope(models.TextChoices):
    INTERNATIONAL = 'INTERNATIONAL', 'International (Org-wide)'
    PROVINCIAL    = 'PROVINCIAL',    'Provincial'
    LOCAL         = 'LOCAL',         'Local (Church)'


class EventStatus(models.TextChoices):
    DRAFT     = 'DRAFT',     'Draft'
    PUBLISHED = 'PUBLISHED', 'Published'
    CANCELLED = 'CANCELLED', 'Cancelled'
    COMPLETED = 'COMPLETED', 'Completed'


class Event(BaseModel):
    """
    A ministry event at any level of the hierarchy.
    """

    # ------------------------------------------------------------------
    # Tenant
    # ------------------------------------------------------------------
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='events',
    )

    # ------------------------------------------------------------------
    # Scope (which tier does this event belong to?)
    # ------------------------------------------------------------------
    scope = models.CharField(
        max_length=20,
        choices=EventScope.choices,
        default=EventScope.LOCAL,
        db_index=True,
    )
    province = models.ForeignKey(
        'organizations.Province',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='events',
        help_text="Populated for PROVINCIAL and LOCAL events.",
    )
    church = models.ForeignKey(
        'organizations.Church',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='events',
        help_text="Populated only for LOCAL events.",
    )

    # ------------------------------------------------------------------
    # Core fields
    # ------------------------------------------------------------------
    title       = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    banner      = models.ImageField(upload_to='events/banners/', null=True, blank=True)

    start_datetime = models.DateTimeField()
    end_datetime   = models.DateTimeField()

    venue_name    = models.CharField(max_length=255, blank=True, default='')
    venue_address = models.TextField(blank=True, default='')
    is_online     = models.BooleanField(default=False)
    stream_url    = models.URLField(blank=True, default='')

    max_attendance = models.PositiveIntegerField(
        default=0,
        help_text="0 = unlimited"
    )

    status = models.CharField(
        max_length=20,
        choices=EventStatus.choices,
        default=EventStatus.DRAFT,
        db_index=True,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_events',
    )

    # ------------------------------------------------------------------
    # Finance stub (Finance module populates)
    # ------------------------------------------------------------------
    budget           = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    finance_metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name        = 'Event'
        verbose_name_plural = 'Events'
        ordering            = ['-start_datetime']
        indexes = [
            models.Index(fields=['organization', 'scope', 'status']),
            models.Index(fields=['start_datetime', 'end_datetime']),
        ]

    def __str__(self) -> str:
        return f"{self.title} [{self.get_scope_display()}] — {self.start_datetime:%Y-%m-%d}"
