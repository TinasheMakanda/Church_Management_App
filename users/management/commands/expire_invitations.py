"""
users/management/commands/expire_invitations.py
------------------------------------------------
Mark PENDING invitations past their expiry time as EXPIRED.
Schedule via cron or Celery beat:

    # crontab — every hour
    0 * * * * cd /app && python manage.py expire_invitations

    # Or add to Celery beat schedule in settings:
    # 'expire-invitations': {
    #     'task': 'onboarding.tasks.expire_invitations_task',
    #     'schedule': crontab(minute=0, hour='*'),
    # }
"""

from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = "Expire all pending invitations that have passed their expiry date."

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run', action='store_true',
            help="Show what would be expired without actually changing anything."
        )

    def handle(self, *args, **options):
        from onboarding.models import Invitation, InvitationStatus

        now     = timezone.now()
        pending = Invitation.objects.filter(
            status=InvitationStatus.PENDING,
            expires_at__lt=now,
        )
        count = pending.count()

        if options['dry_run']:
            self.stdout.write(
                self.style.WARNING(f"[DRY RUN] {count} invitation(s) would be expired.")
            )
            for inv in pending:
                self.stdout.write(f"  • {inv.email} ({inv.role_proffered}) expired at {inv.expires_at}")
            return

        updated = pending.update(status=InvitationStatus.EXPIRED)
        self.stdout.write(
            self.style.SUCCESS(f"✅ Expired {updated} invitation(s).")
        )
