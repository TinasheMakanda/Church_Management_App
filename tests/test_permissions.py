"""
tests/test_permissions.py
--------------------------
Tests for the role-based and tenant permission classes.
"""

import pytest
from rest_framework.test import APIRequestFactory, APIClient
from users.models.roles import Role
from users.permissions import (
    IsSameOrganization,
    IsAdminRole,
    IsChurchAdminOrAbove,
    IsBishopOrAbove,
    IsApostle,
    HasMinimumRole,
    role_rank,
)

pytestmark = pytest.mark.django_db

factory = APIRequestFactory()


def make_request(user, method='get', path='/'):
    request = getattr(factory, method)(path)
    request.user = user
    return request


class TestIsSameOrganization:

    def test_same_org_allowed(self, member_factory, church_factory):
        church = church_factory()
        user   = member_factory(organization=church.organization)
        perm   = IsSameOrganization()
        req    = make_request(user)
        assert perm.has_permission(req, None) is True

    def test_object_same_org_allowed(self, member_factory, church_factory):
        church = church_factory()
        user   = member_factory(organization=church.organization)
        perm   = IsSameOrganization()
        req    = make_request(user)
        assert perm.has_object_permission(req, None, church) is True

    def test_object_different_org_denied(self, member_factory, church_factory):
        church1 = church_factory()
        church2 = church_factory()   # different org (factory creates new org)
        user    = member_factory(organization=church1.organization)
        perm    = IsSameOrganization()
        req     = make_request(user)
        assert perm.has_object_permission(req, None, church2) is False


class TestIsAdminRole:

    @pytest.mark.parametrize('role', [
        Role.SUPER_ADMIN, Role.APOSTLE, Role.ARCH_BISHOP,
        Role.BISHOP, Role.CHURCH_ADMIN,
    ])
    def test_admin_roles_pass(self, user_factory, role):
        user = user_factory(role=role)
        perm = IsAdminRole()
        req  = make_request(user)
        assert perm.has_permission(req, None) is True

    @pytest.mark.parametrize('role', [
        Role.PASTOR, Role.MINISTER, Role.ELDER, Role.DEACON, Role.MEMBER,
    ])
    def test_non_admin_roles_fail(self, user_factory, role):
        user = user_factory(role=role)
        perm = IsAdminRole()
        req  = make_request(user)
        assert perm.has_permission(req, None) is False


class TestHasMinimumRole:

    def test_meets_minimum(self, user_factory):
        user    = user_factory(role=Role.BISHOP)
        PermCls = HasMinimumRole.of(Role.BISHOP)
        perm    = PermCls()
        req     = make_request(user)
        assert perm.has_permission(req, None) is True

    def test_exceeds_minimum(self, user_factory):
        user    = user_factory(role=Role.SUPER_ADMIN)
        PermCls = HasMinimumRole.of(Role.MEMBER)
        perm    = PermCls()
        req     = make_request(user)
        assert perm.has_permission(req, None) is True

    def test_below_minimum(self, user_factory):
        user    = user_factory(role=Role.DEACON)
        PermCls = HasMinimumRole.of(Role.ELDER)
        perm    = PermCls()
        req     = make_request(user)
        assert perm.has_permission(req, None) is False


class TestRoleRank:

    def test_consistent_ordering(self):
        assert role_rank(Role.SUPER_ADMIN) > role_rank(Role.APOSTLE)
        assert role_rank(Role.MEMBER) < role_rank(Role.DEACON)
        assert role_rank(Role.CHURCH_ADMIN) > role_rank(Role.PASTOR)

    def test_unknown_role_returns_minus_one(self):
        assert role_rank('UNKNOWN_ROLE') == -1


class TestTenantScopedEndpoints:
    """
    Verify that cross-tenant data access is blocked at the API layer.
    """

    def test_user_cannot_see_other_org_users(self, user_factory):
        org_a_user = user_factory()
        org_b_user = user_factory()   # different org
        client     = APIClient()
        client.force_authenticate(user=org_a_user)

        response = client.get('/api/auth/users/')
        emails = [u['email'] for u in response.data.get('results', [])]

        assert org_b_user.email not in emails

    def test_user_cannot_see_other_org_churches(self, member_factory, church_factory):
        church_a = church_factory()
        church_b = church_factory()
        user     = member_factory(organization=church_a.organization)
        client   = APIClient()
        client.force_authenticate(user=user)

        response = client.get('/api/organizations/churches/')
        names = [c['name'] for c in response.data.get('results', [])]

        assert church_b.name not in names
