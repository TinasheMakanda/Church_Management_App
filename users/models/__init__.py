"""
users/models/__init__.py
-------------------------
Re-export all user models so Django's app registry picks them up
and callers can simply do:

    from users.models import User, UserProfile, Role
"""

from .roles import Role, ADMIN_ROLES, INVITER_ROLES, ROLE_SCOPE
from .user import User
from .profile import UserProfile

__all__ = [
    'Role',
    'ADMIN_ROLES',
    'INVITER_ROLES',
    'ROLE_SCOPE',
    'User',
    'UserProfile',
]
