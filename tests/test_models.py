"""
tests/test_models.py
---------------------
Unit tests for model-level business logic.
No HTTP layer — pure model/ORM tests.
"""

import pytest
from django.utils import timezone
from datetime import timedelta

from users.models.roles import Role, ADMIN_ROLES, INVITER_ROLES, role_rank
from onboarding.models import InvitationStatus

pytestmark = pytest.mark.django_db


# ===========================================================================
# Role helpers
# ===========================================================================

class TestRoleHierarchy:

    def test_super_admin_is_highest_rank(self):
        from users.permissions import role_rank
        assert role_rank(Role.SUPER_ADMIN) > role_rank(Role.APOSTLE)
        assert role_rank(Role.APOSTLE) > role_rank(Role.ARCH_BISHOP)
        assert role_rank(Role.ARCH_BISHOP) > role_rank(Role.BISHOP)
        assert role_rank(Role.BISHOP) > role_rank(Role.CHURCH_ADMIN)
        assert role_rank(Role.CHURCH_ADMIN) > role_rank(Role.PASTOR)
        assert role_rank(Role.MEMBER) == 0

    def test_admin_roles_set(self):
        assert Role.SUPER_ADMIN in ADMIN_ROLES
        assert Role.MEMBER not in ADMIN_ROLES

    def test_inviter_roles_superset_of_admin_roles(self):
        assert ADMIN_ROLES.issubset(INVITER_ROLES)
        assert Role.PASTOR in INVITER_ROLES
        assert Role.DEACON not in INVITER_ROLES


# ===========================================================================
# User model
# ===========================================================================

class TestUserModel:

    def test_full_name(self, user_factory):
        user = user_factory(first_name='John', last_name='Doe')
        assert user.full_name == 'John Doe'

    def test_full_name_falls_back_to_email(self, user_factory):
        user = user_factory(first_name='', last_name='')
        assert user.full_name == user.email

    def test_is_admin_role_true_for_admin(self, user_factory):
        user = user_factory(role=Role.CHURCH_ADMIN)
        assert user.is_admin_role is True

    def test_is_admin_role_false_for_member(self, user_factory):
        user = user_factory(role=Role.MEMBER)
        assert user.is_admin_role is False

    def test_can_invite_pastor(self, user_factory):
        user = user_factory(role=Role.PASTOR)
        assert user.can_invite is True

    def test_cannot_invite_deacon(self, user_factory):
        user = user_factory(role=Role.DEACON)
        assert user.can_invite is False

    def test_str_representation(self, user_factory):
        user = user_factory(first_name='Jane', last_name='Smith',
                            email='jane@church.org', role=Role.ELDER)
        assert 'Jane Smith' in str(user)
        assert 'jane@church.org' in str(user)
        assert 'Elder' in str(user)

    def test_profile_auto_created(self, user_factory):
        """Signal should auto-create a UserProfile."""
        from users.models import UserProfile
        user = user_factory()
        assert UserProfile.objects.filter(user=user).exists()


# ===========================================================================
# Organization model
# ===========================================================================

class TestOrganizationModel:

    def test_str(self, org_factory):
        org = org_factory(name='Grace Fellowship')
        assert str(org) == 'Grace Fellowship'

    def test_slug_unique(self, org_factory):
        from django.db import IntegrityError
        org_factory(slug='test-slug')
        with pytest.raises(IntegrityError):
            org_factory(slug='test-slug')


# ===========================================================================
# Invitation model
# ===========================================================================

class TestInvitationModel:

    def test_is_valid_for_pending_future(self, invitation_factory):
        inv = invitation_factory(
            status=InvitationStatus.PENDING,
            expires_at=timezone.now() + timedelta(days=3),
        )
        assert inv.is_valid is True

    def test_is_not_valid_if_expired(self, invitation_factory):
        inv = invitation_factory(
            status=InvitationStatus.PENDING,
            expires_at=timezone.now() - timedelta(seconds=1),
        )
        assert inv.is_valid is False

    def test_is_not_valid_if_revoked(self, invitation_factory):
        inv = invitation_factory(status=InvitationStatus.REVOKED)
        assert inv.is_valid is False

    def test_is_not_valid_if_accepted(self, invitation_factory):
        inv = invitation_factory(status=InvitationStatus.ACCEPTED)
        assert inv.is_valid is False

    def test_accept_stamps_user(self, invitation_factory, user_factory):
        inv  = invitation_factory()
        user = user_factory()
        inv.accept(user)
        inv.refresh_from_db()
        assert inv.status     == InvitationStatus.ACCEPTED
        assert inv.accepted_by == user
        assert inv.accepted_at is not None

    def test_revoke(self, invitation_factory):
        inv = invitation_factory()
        inv.revoke()
        inv.refresh_from_db()
        assert inv.status == InvitationStatus.REVOKED

    def test_invite_url_contains_token(self, invitation_factory, settings):
        settings.FRONTEND_BASE_URL = 'https://app.church.org'
        inv = invitation_factory()
        assert str(inv.token) in inv.invite_url
        assert 'https://app.church.org' in inv.invite_url


# ===========================================================================
# Hierarchy — Region, Province, Church
# ===========================================================================

class TestHierarchyModels:

    def test_region_belongs_to_org(self, region_factory):
        region = region_factory()
        assert region.organization is not None

    def test_province_links_to_region(self, province_factory):
        province = province_factory()
        assert province.region is not None
        assert province.organization == province.region.organization

    def test_church_links_to_province(self, church_factory):
        church = church_factory()
        assert church.province is not None
        assert church.organization == church.province.organization

    def test_church_str(self, church_factory):
        church = church_factory(name='Hope Church')
        assert 'Hope Church' in str(church)


# ===========================================================================
# Event scope validation
# ===========================================================================

class TestEventScope:

    def test_local_event_has_church(self, event_factory):
        event = event_factory()
        assert event.church is not None

    def test_international_event_has_no_church(self, international_event_factory):
        event = international_event_factory()
        assert event.church is None
        assert event.province is None
