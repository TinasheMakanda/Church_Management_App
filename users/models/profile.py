"""
users/models/profile.py
------------------------
UserProfile extends User with ministry-specific details that don't
belong on the core auth model.

Kept separate so the auth system stays lean and profile data can
be loaded lazily (select_related('profile')).
"""

from django.db import models
from django.conf import settings
from chms.base_models import BaseModel


class UserProfile(BaseModel):
    """
    One-to-one extension of the User model.

    Ministry details
    ----------------
    * ordination_date  — when the minister/pastor was ordained
    * ministry_title   — free-text title, e.g. 'Worship Leader', 'Youth Pastor'
    * assigned_church  — the Church this user is primarily attached to
    * assigned_region  — for Arch Bishops
    * assigned_province — for Bishops

    Social / emergency
    ------------------
    * social links, emergency contact — common pastoral record needs
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
        primary_key=False,       # UUID PK comes from BaseModel
    )

    # ------------------------------------------------------------------
    # Ministry details
    # ------------------------------------------------------------------
    ministry_title   = models.CharField(max_length=150, blank=True, default='')
    ordination_date  = models.DateField(null=True, blank=True)

    assigned_church  = models.ForeignKey(
        'organizations.Church',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='members',
    )
    assigned_province = models.ForeignKey(
        'organizations.Province',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='province_members',
    )
    assigned_region   = models.ForeignKey(
        'organizations.Region',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='region_members',
    )

    # ------------------------------------------------------------------
    # Social
    # ------------------------------------------------------------------
    facebook_url  = models.URLField(blank=True, default='')
    instagram_url = models.URLField(blank=True, default='')
    twitter_url   = models.URLField(blank=True, default='')
    youtube_url   = models.URLField(blank=True, default='')

    # ------------------------------------------------------------------
    # Emergency contact
    # ------------------------------------------------------------------
    emergency_contact_name     = models.CharField(max_length=255, blank=True, default='')
    emergency_contact_phone    = models.CharField(max_length=30, blank=True, default='')
    emergency_contact_relation = models.CharField(max_length=100, blank=True, default='')

    class Meta:
        verbose_name        = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self) -> str:
        return f"Profile — {self.user.full_name}"
