"""
users/models/roles.py
----------------------
Centralised role definitions for the entire CHMS platform.

The hierarchy flows top-down:
    SUPER_ADMIN
        └── APOSTLE
                └── ARCH_BISHOP   (leads a Region)
                        └── BISHOP          (leads a Province)
                                └── CHURCH_ADMIN    (leads a Church)
                                        ├── PASTOR
                                        ├── MINISTER
                                        ├── ELDER
                                        ├── DEACON
                                        └── MEMBER

Roles are stored as a single CharField on the User model.
Permission logic (what each role can do) lives in
`users/permissions.py` using Django's permission framework.
"""

from django.db import models


class Role(models.TextChoices):
    # ------------------------------------------------------------------
    # Platform / Network-wide
    # ------------------------------------------------------------------
    SUPER_ADMIN  = 'SUPER_ADMIN',  'Super Admin'
    APOSTLE      = 'APOSTLE',      'Apostle'

    # ------------------------------------------------------------------
    # Regional tier
    # ------------------------------------------------------------------
    ARCH_BISHOP  = 'ARCH_BISHOP',  'Arch Bishop'

    # ------------------------------------------------------------------
    # Provincial tier
    # ------------------------------------------------------------------
    BISHOP       = 'BISHOP',       'Bishop'

    # ------------------------------------------------------------------
    # Local church tier
    # ------------------------------------------------------------------
    CHURCH_ADMIN = 'CHURCH_ADMIN', 'Church Admin'
    PASTOR       = 'PASTOR',       'Pastor'
    MINISTER     = 'MINISTER',     'Minister'
    ELDER        = 'ELDER',        'Elder'
    DEACON       = 'DEACON',       'Deacon'
    MEMBER       = 'MEMBER',       'Member'


# Convenience: roles that have administrative privileges at their tier
ADMIN_ROLES = {
    Role.SUPER_ADMIN,
    Role.APOSTLE,
    Role.ARCH_BISHOP,
    Role.BISHOP,
    Role.CHURCH_ADMIN,
}

# Roles that can invite others into the system
INVITER_ROLES = ADMIN_ROLES | {Role.PASTOR}

# Role → maximum scope that role can manage
ROLE_SCOPE = {
    Role.SUPER_ADMIN:  'organization',
    Role.APOSTLE:      'organization',
    Role.ARCH_BISHOP:  'region',
    Role.BISHOP:       'province',
    Role.CHURCH_ADMIN: 'church',
    Role.PASTOR:       'church',
    Role.MINISTER:     'church',
    Role.ELDER:        'church',
    Role.DEACON:       'church',
    Role.MEMBER:       'church',
}
