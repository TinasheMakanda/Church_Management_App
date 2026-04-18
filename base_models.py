"""
chms/base_models.py
-------------------
Abstract base classes shared across ALL apps.
"""

import uuid
from django.db import models


class UUIDModel(models.Model):
    """Primary key is a UUID instead of an auto-integer."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class TimeStampedModel(models.Model):
    """Adds created_at / updated_at to any model."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class BaseModel(UUIDModel, TimeStampedModel):
    """
    The standard base for every CHMS model.
    Combines UUID PK + automatic timestamps.
    """
    class Meta:
        abstract = True
