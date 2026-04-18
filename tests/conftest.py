"""
tests/conftest.py
------------------
Pytest fixtures that provide factory callables to all test modules.
Using fixtures instead of importing factories directly allows pytest
to inject the django_db marker automatically.
"""

import pytest
from tests.factories import (
    OrganizationFactory,
    RegionFactory,
    ProvinceFactory,
    ChurchFactory,
    UserFactory,
    SuperAdminFactory,
    ApostleFactory,
    ArchBishopFactory,
    BishopFactory,
    ChurchAdminFactory,
    PastorFactory,
    MemberFactory,
    InvitationFactory,
    ExpiredInvitationFactory,
    ChurchGroupFactory,
    TaskforceFactory,
    WorshipTeamFactory,
    GroupMembershipFactory,
    EventFactory,
    InternationalEventFactory,
    ProvincialEventFactory,
)


# ---------------------------------------------------------------------------
# Organization fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def org_factory(db):
    return OrganizationFactory

@pytest.fixture
def region_factory(db):
    return RegionFactory

@pytest.fixture
def province_factory(db):
    return ProvinceFactory

@pytest.fixture
def church_factory(db):
    return ChurchFactory


# ---------------------------------------------------------------------------
# User fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def user_factory(db):
    return UserFactory

@pytest.fixture
def super_admin_factory(db):
    return SuperAdminFactory

@pytest.fixture
def apostle_factory(db):
    return ApostleFactory

@pytest.fixture
def arch_bishop_factory(db):
    return ArchBishopFactory

@pytest.fixture
def bishop_factory(db):
    return BishopFactory

@pytest.fixture
def church_admin_factory(db):
    return ChurchAdminFactory

@pytest.fixture
def pastor_factory(db):
    return PastorFactory

@pytest.fixture
def member_factory(db):
    return MemberFactory


# ---------------------------------------------------------------------------
# Onboarding fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def invitation_factory(db):
    return InvitationFactory

@pytest.fixture
def expired_invitation_factory(db):
    return ExpiredInvitationFactory


# ---------------------------------------------------------------------------
# Group fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def group_factory(db):
    return ChurchGroupFactory

@pytest.fixture
def taskforce_factory(db):
    return TaskforceFactory

@pytest.fixture
def worship_team_factory(db):
    return WorshipTeamFactory

@pytest.fixture
def membership_factory(db):
    return GroupMembershipFactory


# ---------------------------------------------------------------------------
# Event fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def event_factory(db):
    return EventFactory

@pytest.fixture
def international_event_factory(db):
    return InternationalEventFactory

@pytest.fixture
def provincial_event_factory(db):
    return ProvincialEventFactory


# ---------------------------------------------------------------------------
# Convenience: pre-built single instances
# ---------------------------------------------------------------------------

@pytest.fixture
def organization(db):
    return OrganizationFactory()

@pytest.fixture
def super_admin(db, organization):
    return SuperAdminFactory(organization=organization)

@pytest.fixture
def church(db):
    return ChurchFactory()

@pytest.fixture
def church_admin(db, church):
    return ChurchAdminFactory(organization=church.organization)

@pytest.fixture
def member(db, church):
    return MemberFactory(organization=church.organization)
