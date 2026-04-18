"""
users/signals.py
-----------------
Signal handlers for the users app.

auto-create UserProfile
------------------------
Every time a User is saved for the first time (created=True),
we automatically create a matching UserProfile. This means callers
never need to remember to do it manually.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a blank UserProfile whenever a new User is saved."""
    if created:
        from users.models import UserProfile
        UserProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    """Ensure the profile is saved alongside the user."""
    if hasattr(instance, 'profile'):
        instance.profile.save()
