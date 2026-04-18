"""
tests/test_onboarding.py
-------------------------
Integration tests for the invitation send → validate → accept flow.
Uses DRF's APIClient to exercise the full HTTP stack.
"""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.utils import timezone
from datetime import timedelta

from users.models import User
from users.models.roles import Role
from onboarding.models import Invitation, InvitationStatus

pytestmark = pytest.mark.django_db


# ===========================================================================
# Helpers
# ===========================================================================

def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


# ===========================================================================
# POST /api/onboarding/invitations/ — sending an invitation
# ===========================================================================

class TestSendInvitation:

    def test_church_admin_can_invite_member(
        self, church_admin_factory, church_factory
    ):
        church = church_factory()
        admin  = church_admin_factory(organization=church.organization)
        client = auth_client(admin)

        response = client.post('/api/onboarding/invitations/', {
            'email':            'newmember@test.org',
            'role_proffered':   Role.MEMBER,
            'target_entity_id': str(church.id),
        }, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert Invitation.objects.filter(
            email='newmember@test.org',
            role_proffered=Role.MEMBER,
        ).exists()

    def test_member_cannot_send_invitation(self, member_factory):
        member = member_factory()
        client = auth_client(member)

        response = client.post('/api/onboarding/invitations/', {
            'email':          'someone@test.org',
            'role_proffered': Role.MEMBER,
        }, format='json')

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_cannot_invite_to_equal_or_higher_role(self, church_admin_factory):
        admin  = church_admin_factory()
        client = auth_client(admin)

        # Church Admin trying to invite another Church Admin — same rank, forbidden
        response = client.post('/api/onboarding/invitations/', {
            'email':            'other@test.org',
            'role_proffered':   Role.CHURCH_ADMIN,
            'target_entity_id': str(admin.organization.id),
        }, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_duplicate_pending_invitation_rejected(
        self, church_admin_factory, church_factory, invitation_factory
    ):
        church = church_factory()
        admin  = church_admin_factory(organization=church.organization)
        invitation_factory(
            organization=church.organization,
            email='dup@test.org',
            role_proffered=Role.MEMBER,
            status=InvitationStatus.PENDING,
            invited_by=admin,
        )
        client = auth_client(admin)
        response = client.post('/api/onboarding/invitations/', {
            'email':            'dup@test.org',
            'role_proffered':   Role.MEMBER,
            'target_entity_id': str(church.id),
        }, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_missing_target_entity_for_scoped_role(self, bishop_factory):
        bishop = bishop_factory()
        client = auth_client(bishop)

        response = client.post('/api/onboarding/invitations/', {
            'email':          'newchurchadmin@test.org',
            'role_proffered': Role.CHURCH_ADMIN,
            # target_entity_id intentionally omitted
        }, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_unauthenticated_cannot_send(self):
        client = APIClient()
        response = client.post('/api/onboarding/invitations/', {
            'email':          'anon@test.org',
            'role_proffered': Role.MEMBER,
        }, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN


# ===========================================================================
# GET /api/onboarding/validate/{token}/ — token validation
# ===========================================================================

class TestValidateToken:

    def test_valid_token_returns_invitation_info(self, invitation_factory):
        inv    = invitation_factory()
        client = APIClient()  # public endpoint

        response = client.get(f'/api/onboarding/validate/{inv.token}/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == inv.email
        assert response.data['role']  == inv.role_proffered

    def test_invalid_token_returns_404(self):
        import uuid
        client   = APIClient()
        response = client.get(f'/api/onboarding/validate/{uuid.uuid4()}/')
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_expired_token_returns_410(self, invitation_factory):
        inv = invitation_factory(
            status=InvitationStatus.PENDING,
            expires_at=timezone.now() - timedelta(days=1),
        )
        client   = APIClient()
        response = client.get(f'/api/onboarding/validate/{inv.token}/')
        assert response.status_code == status.HTTP_410_GONE

    def test_revoked_token_returns_410(self, invitation_factory):
        inv = invitation_factory(status=InvitationStatus.REVOKED)
        client   = APIClient()
        response = client.get(f'/api/onboarding/validate/{inv.token}/')
        assert response.status_code == status.HTTP_410_GONE


# ===========================================================================
# POST /api/onboarding/accept/ — accept & register
# ===========================================================================

class TestAcceptInvitation:

    def test_valid_acceptance_creates_user(self, invitation_factory):
        inv    = invitation_factory(email='newuser@church.org', role_proffered=Role.MEMBER)
        client = APIClient()

        response = client.post('/api/onboarding/accept/', {
            'token':      str(inv.token),
            'first_name': 'Grace',
            'last_name':  'Dlamini',
            'password':   'Secure1234!',
        }, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(email='newuser@church.org').exists()

        inv.refresh_from_db()
        assert inv.status == InvitationStatus.ACCEPTED

    def test_accept_sets_correct_role(self, invitation_factory):
        inv    = invitation_factory(role_proffered=Role.ELDER)
        client = APIClient()

        client.post('/api/onboarding/accept/', {
            'token':      str(inv.token),
            'first_name': 'Samuel',
            'last_name':  'Nkosi',
            'password':   'Secure1234!',
        }, format='json')

        user = User.objects.get(email=inv.email)
        assert user.role == Role.ELDER

    def test_accept_sets_correct_organization(self, invitation_factory):
        inv    = invitation_factory()
        client = APIClient()

        client.post('/api/onboarding/accept/', {
            'token':      str(inv.token),
            'first_name': 'Mary',
            'last_name':  'Mokoena',
            'password':   'Secure1234!',
        }, format='json')

        user = User.objects.get(email=inv.email)
        assert user.organization == inv.organization

    def test_invalid_token_rejected(self):
        import uuid
        client   = APIClient()
        response = client.post('/api/onboarding/accept/', {
            'token':      str(uuid.uuid4()),
            'first_name': 'X',
            'last_name':  'Y',
            'password':   'Secure1234!',
        }, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_already_accepted_token_rejected(self, invitation_factory, member_factory):
        user = member_factory()
        inv  = invitation_factory(status=InvitationStatus.ACCEPTED, accepted_by=user)
        client = APIClient()

        response = client.post('/api/onboarding/accept/', {
            'token':      str(inv.token),
            'first_name': 'Another',
            'last_name':  'Person',
            'password':   'Secure1234!',
        }, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_short_password_rejected(self, invitation_factory):
        inv    = invitation_factory()
        client = APIClient()

        response = client.post('/api/onboarding/accept/', {
            'token':      str(inv.token),
            'first_name': 'Test',
            'last_name':  'User',
            'password':   'short',
        }, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ===========================================================================
# DELETE /api/onboarding/invitations/{id}/ — revoke
# ===========================================================================

class TestRevokeInvitation:

    def test_admin_can_revoke_pending(self, church_admin_factory, invitation_factory):
        admin  = church_admin_factory()
        inv    = invitation_factory(organization=admin.organization, invited_by=admin)
        client = auth_client(admin)

        response = client.delete(f'/api/onboarding/invitations/{inv.id}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT

        inv.refresh_from_db()
        assert inv.status == InvitationStatus.REVOKED

    def test_cannot_revoke_accepted(self, church_admin_factory, invitation_factory, member_factory):
        admin  = church_admin_factory()
        member = member_factory(organization=admin.organization)
        inv    = invitation_factory(
            organization=admin.organization,
            invited_by=admin,
            status=InvitationStatus.ACCEPTED,
            accepted_by=member,
        )
        client = auth_client(admin)

        response = client.delete(f'/api/onboarding/invitations/{inv.id}/')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
