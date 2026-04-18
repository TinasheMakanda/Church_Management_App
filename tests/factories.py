"""
tests/factories.py
-------------------
factory_boy factories for every major model.
Import these in test files instead of creating objects manually.

Usage:
    from tests.factories import UserFactory, ChurchFactory

    def test_something():
        church = ChurchFactory()
        user   = UserFactory(organization=church.organization, role='MEMBER')
        user.profile.assigned_church = church
        user.profile.save()
"""

import factory
import factory.django
from django.utils import timezone
from datetime import timedelta

from users.models import User, UserProfile
from users.models.roles import Role
from organizations.models import Organization, Region, Province, Church
from onboarding.models import Invitation, InvitationStatus
from groups.models import ChurchGroup, GroupMembership, GroupType
from events.models import Event, EventScope, EventStatus


# ---------------------------------------------------------------------------
# Organizations
# ---------------------------------------------------------------------------

class OrganizationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Organization

    name    = factory.Sequence(lambda n: f"Church Network {n}")
    slug    = factory.Sequence(lambda n: f"church-network-{n}")
    country = "South Africa"
    status  = Organization.Status.ACTIVE


class RegionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Region

    organization = factory.SubFactory(OrganizationFactory)
    name         = factory.Sequence(lambda n: f"Region {n}")
    is_active    = True


class ProvinceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Province

    organization = factory.LazyAttribute(lambda o: o.region.organization)
    region       = factory.SubFactory(RegionFactory)
    name         = factory.Sequence(lambda n: f"Province {n}")
    is_active    = True


class ChurchFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Church

    organization = factory.LazyAttribute(lambda o: o.province.organization)
    province     = factory.SubFactory(ProvinceFactory)
    name         = factory.Sequence(lambda n: f"Church {n}")
    city         = "Johannesburg"
    is_active    = True


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email        = factory.Sequence(lambda n: f"user{n}@testchurch.org")
    username     = factory.Sequence(lambda n: f"user{n}")
    first_name   = "Test"
    last_name    = factory.Sequence(lambda n: f"User{n}")
    password     = factory.PostGenerationMethodCall('set_password', 'testpass123')
    organization = factory.SubFactory(OrganizationFactory)
    role         = Role.MEMBER
    is_active    = True


class SuperAdminFactory(UserFactory):
    role         = Role.SUPER_ADMIN
    is_staff     = True
    is_superuser = True


class ApostleFactory(UserFactory):
    role = Role.APOSTLE


class ArchBishopFactory(UserFactory):
    role = Role.ARCH_BISHOP


class BishopFactory(UserFactory):
    role = Role.BISHOP


class ChurchAdminFactory(UserFactory):
    role = Role.CHURCH_ADMIN


class PastorFactory(UserFactory):
    role = Role.PASTOR


class MemberFactory(UserFactory):
    role = Role.MEMBER


# ---------------------------------------------------------------------------
# Onboarding
# ---------------------------------------------------------------------------

class InvitationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Invitation

    organization     = factory.SubFactory(OrganizationFactory)
    email            = factory.Sequence(lambda n: f"invitee{n}@testchurch.org")
    role_proffered   = Role.MEMBER
    invited_by       = factory.SubFactory(ChurchAdminFactory,
                                          organization=factory.SelfAttribute('..organization'))
    status           = InvitationStatus.PENDING
    expires_at       = factory.LazyFunction(lambda: timezone.now() + timedelta(days=7))


class ExpiredInvitationFactory(InvitationFactory):
    expires_at = factory.LazyFunction(lambda: timezone.now() - timedelta(days=1))
    status     = InvitationStatus.EXPIRED


# ---------------------------------------------------------------------------
# Groups
# ---------------------------------------------------------------------------

class ChurchGroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ChurchGroup

    organization = factory.LazyAttribute(lambda o: o.church.organization)
    church       = factory.SubFactory(ChurchFactory)
    group_type   = GroupType.HOME_GROUP
    name         = factory.Sequence(lambda n: f"Group {n}")
    is_active    = True


class TaskforceFactory(ChurchGroupFactory):
    group_type = GroupType.TASKFORCE


class WorshipTeamFactory(ChurchGroupFactory):
    group_type = GroupType.WORSHIP_TEAM


class GroupMembershipFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = GroupMembership

    group        = factory.SubFactory(ChurchGroupFactory)
    user         = factory.SubFactory(MemberFactory,
                                      organization=factory.SelfAttribute('..group.organization'))
    is_co_leader = False


# ---------------------------------------------------------------------------
# Events
# ---------------------------------------------------------------------------

class EventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Event

    organization    = factory.SubFactory(OrganizationFactory)
    title           = factory.Sequence(lambda n: f"Event {n}")
    scope           = EventScope.LOCAL
    church          = factory.SubFactory(ChurchFactory,
                                         organization=factory.SelfAttribute('..organization'))
    province        = factory.LazyAttribute(lambda o: o.church.province)
    start_datetime  = factory.LazyFunction(lambda: timezone.now() + timedelta(days=7))
    end_datetime    = factory.LazyFunction(lambda: timezone.now() + timedelta(days=7, hours=3))
    status          = EventStatus.DRAFT
    created_by      = factory.SubFactory(ChurchAdminFactory,
                                         organization=factory.SelfAttribute('..organization'))


class InternationalEventFactory(EventFactory):
    scope    = EventScope.INTERNATIONAL
    church   = None
    province = None


class ProvincialEventFactory(EventFactory):
    scope  = EventScope.PROVINCIAL
    church = None
