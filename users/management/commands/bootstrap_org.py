"""
users/management/commands/bootstrap_org.py
------------------------------------------
One-time command to create the first Organization and its SUPER_ADMIN.
Run this on a fresh database before anything else.

Usage:
    python manage.py bootstrap_org \
        --org-name  "My Church Network" \
        --org-slug  "my-church-network" \
        --admin-email "admin@mychurch.org" \
        --admin-first "John" \
        --admin-last  "Doe"

The command will prompt for a password securely.
If --no-input is passed, a random password is generated and printed once.
"""

import secrets
import string

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction


class Command(BaseCommand):
    help = "Bootstrap a new Organization with its first Super Admin user."

    def add_arguments(self, parser):
        parser.add_argument('--org-name',     required=True,  help="Full organization name")
        parser.add_argument('--org-slug',     required=True,  help="URL-safe slug for the org")
        parser.add_argument('--org-country',  default='',     help="Country (optional)")
        parser.add_argument('--admin-email',  required=True,  help="Super Admin email")
        parser.add_argument('--admin-first',  required=True,  help="Super Admin first name")
        parser.add_argument('--admin-last',   required=True,  help="Super Admin last name")
        parser.add_argument('--no-input',     action='store_true',
                            help="Skip password prompt and generate a random password")

    def handle(self, *args, **options):
        from organizations.models import Organization
        from users.models import User
        from users.models.roles import Role

        org_name    = options['org_name']
        org_slug    = options['org_slug']
        admin_email = options['admin_email']

        # --- Guard: prevent duplicate slugs ---
        if Organization.objects.filter(slug=org_slug).exists():
            raise CommandError(f"An Organization with slug '{org_slug}' already exists.")

        if User.objects.filter(email=admin_email).exists():
            raise CommandError(f"A user with email '{admin_email}' already exists.")

        # --- Password ---
        if options['no_input']:
            alphabet = string.ascii_letters + string.digits + '!@#$%^&*()'
            password = ''.join(secrets.choice(alphabet) for _ in range(20))
            self.stdout.write(self.style.WARNING(
                f"\n⚠️  Generated password (save this — shown only once): {password}\n"
            ))
        else:
            import getpass
            password = getpass.getpass(f"Password for {admin_email}: ")
            confirm  = getpass.getpass("Confirm password: ")
            if password != confirm:
                raise CommandError("Passwords do not match.")
            if len(password) < 8:
                raise CommandError("Password must be at least 8 characters.")

        # --- Create in a transaction so we never end up with a partial state ---
        with transaction.atomic():
            org = Organization.objects.create(
                name    = org_name,
                slug    = org_slug,
                country = options.get('org_country', ''),
            )
            self.stdout.write(f"✅ Organization created: {org.name} (id={org.id})")

            admin = User.objects.create_superuser(
                email      = admin_email,
                password   = password,
                first_name = options['admin_first'],
                last_name  = options['admin_last'],
                role       = Role.SUPER_ADMIN,
                organization = org,
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ Super Admin created: {admin.full_name} <{admin.email}>\n"
                    f"   Organization: {org.name}\n"
                    f"   Organization ID: {org.id}\n"
                    f"   User ID: {admin.id}\n\n"
                    f"   Next step: log in and send your first Apostle invitation.\n"
                )
            )
