"""
groups/models/group.py
-----------------------
ChurchGroup is the flexible container for:
  * Home Groups     — cell / connect groups
  * Taskforces      — project or ministry teams (can be linked to Events)
  * Worship Teams   — music / creative teams

Multi-tenancy: every group is scoped to an Organization AND a Church.

Event linkage
-------------
The `events` M2M is intentionally on the Group side so that:
  - A Taskforce can be listed as "Organizer" of multiple events
  - An Event can have multiple organizing Taskforces
This satisfies the "ChurchGroups linked to Events as Organizers" requirement.
"""

from django.conf import settings
from django.db import models
from chms.base_models import BaseModel


class GroupType(models.TextChoices):
    HOME_GROUP    = 'HOME_GROUP',    'Home Group'
    TASKFORCE     = 'TASKFORCE',     'Taskforce'
    WORSHIP_TEAM  = 'WORSHIP_TEAM',  'Worship Team'
    OTHER         = 'OTHER',         'Other'


class ChurchGroup(BaseModel):
    """
    A ministry group within a Church.
    """

    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='groups',
    )
    church = models.ForeignKey(
        'organizations.Church',
        on_delete=models.CASCADE,
        related_name='groups',
    )
    leader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='led_groups',
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='GroupMembership',
        related_name='church_groups',
        blank=True,
    )

    # Event linkage — Taskforces (and other groups) can organise events
    events = models.ManyToManyField(
        'events.Event',
        related_name='organizer_groups',
        blank=True,
        help_text="Events this group is responsible for organising.",
    )

    group_type  = models.CharField(max_length=30, choices=GroupType.choices,
                                   default=GroupType.OTHER, db_index=True)
    name        = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    is_active   = models.BooleanField(default=True)

    # Meeting details
    meeting_day      = models.CharField(max_length=20, blank=True, default='')
    meeting_time     = models.TimeField(null=True, blank=True)
    meeting_location = models.TextField(blank=True, default='')
    meeting_online   = models.BooleanField(default=False)
    meeting_url      = models.URLField(blank=True, default='')

    class Meta:
        verbose_name        = 'Church Group'
        verbose_name_plural = 'Church Groups'
        ordering            = ['church', 'group_type', 'name']
        unique_together     = [('church', 'name')]

    def __str__(self) -> str:
        return f"{self.name} ({self.get_group_type_display()}) — {self.church.name}"


class GroupMembership(BaseModel):
    """
    Through table for ChurchGroup ↔ User membership.
    Tracks join date and whether the member is a co-leader.
    """

    group  = models.ForeignKey(ChurchGroup, on_delete=models.CASCADE)
    user   = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    joined = models.DateField(auto_now_add=True)
    is_co_leader = models.BooleanField(default=False)
    notes  = models.TextField(blank=True, default='')

    class Meta:
        verbose_name        = 'Group Membership'
        verbose_name_plural = 'Group Memberships'
        unique_together     = [('group', 'user')]

    def __str__(self) -> str:
        return f"{self.user.full_name} in {self.group.name}"
