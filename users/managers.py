"""
users/managers.py
------------------
Custom manager for the User model.

Overrides create_user / create_superuser to:
  * Use email as the unique identifier (not username)
  * Auto-populate username from the email prefix if not supplied
  * Enforce that SUPER_ADMIN users have is_staff=True and is_superuser=True
"""

from django.contrib.auth.base_user import BaseUserManager
from django.utils.text import slugify


class UserManager(BaseUserManager):

    def _generate_username(self, email: str) -> str:
        """
        Derive a unique username from the email prefix.
        e.g. 'john.doe@rccg.org' → 'john.doe' (with numeric suffix if taken)
        """
        base = slugify(email.split('@')[0])
        username = base
        n = 1
        while self.model.objects.filter(username=username).exists():
            username = f"{base}{n}"
            n += 1
        return username

    def create_user(self, email: str, password: str = None, **extra_fields):
        if not email:
            raise ValueError("An email address is required.")
        email = self.normalize_email(email)
        extra_fields.setdefault('username', self._generate_username(email))
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, password: str, **extra_fields):
        from users.models.roles import Role
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', Role.SUPER_ADMIN)

        if not extra_fields.get('is_staff'):
            raise ValueError("Superuser must have is_staff=True.")
        if not extra_fields.get('is_superuser'):
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)
