# CHMS — Church Management System

A multi-tenant Django REST API for managing church networks of any size.  
One deployment serves many independent church organisations, each fully isolated.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Project Structure](#project-structure)
3. [Setup & Installation](#setup--installation)
4. [The Hierarchy](#the-hierarchy)
5. [Role System](#role-system)
6. [Invitation & Onboarding Flow](#invitation--onboarding-flow)
7. [API Reference](#api-reference)
8. [Permissions Matrix](#permissions-matrix)
9. [Future Modules](#future-modules)
10. [Running Tests](#running-tests)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                    Organization                      │  ← Tenant root
│                                                     │
│   ┌──────────────┐   ┌──────────────┐              │
│   │    Region     │   │    Region     │  ← Arch Bishops
│   │               │   │               │              │
│   │ ┌──────────┐ │   │ ┌──────────┐ │              │
│   │ │ Province │ │   │ │ Province │ │  ← Bishops   │
│   │ │          │ │   │ │          │ │              │
│   │ │ ┌──────┐ │ │   │ │ ┌──────┐ │ │              │
│   │ │ │Church│ │ │   │ │ │Church│ │ │  ← Admins   │
│   │ │ └──────┘ │ │   │ │ └──────┘ │ │              │
│   │ └──────────┘ │   │ └──────────┘ │              │
│   └──────────────┘   └──────────────┘              │
└─────────────────────────────────────────────────────┘
```

**Multi-tenancy:** Every model carries an `organization` FK. No query ever crosses tenant boundaries — all ViewSet querysets are pre-filtered to `request.user.organization`.

**Modular models:** Every app uses a `models/` package instead of a flat `models.py`. Models are split by domain concern.

---

## Project Structure

```
chms/
├── chms/                       # Django project package
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── base_models.py          # UUIDModel, TimeStampedModel, BaseModel
│
├── users/                      # Custom User, Profiles, Permissions
│   ├── models/
│   │   ├── __init__.py         # re-exports: User, UserProfile, Role
│   │   ├── roles.py            # Role TextChoices + helper sets
│   │   ├── user.py             # Custom AbstractUser
│   │   └── profile.py          # UserProfile (1:1 extension)
│   ├── managers.py             # Email-based UserManager
│   ├── permissions.py          # DRF permission classes (role + tenant)
│   ├── querysets.py            # TenantQuerySet / TenantManager
│   ├── signals.py              # Auto-create UserProfile on User save
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   └── management/
│       └── commands/
│           ├── bootstrap_org.py        # First org + super admin
│           └── expire_invitations.py   # Cron/beat cleanup
│
├── organizations/              # Org, Region, Province, Church
│   ├── models/
│   │   ├── __init__.py         # re-exports all 4 models
│   │   ├── organization.py     # Tenant root
│   │   └── hierarchy.py        # Region, Province, Church
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
│
├── onboarding/                 # Invitation tokens & acceptance
│   ├── models/
│   │   ├── __init__.py
│   │   └── invitation.py       # Invitation with UUID token
│   ├── serializers.py          # Send + Accept serializers
│   ├── views.py                # InvitationViewSet + public accept/validate
│   ├── urls.py
│   └── admin.py
│
├── groups/                     # Home Groups, Taskforces, Worship Teams
│   ├── models/
│   │   ├── __init__.py
│   │   └── group.py            # ChurchGroup + GroupMembership
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
│
├── events/                     # International / Provincial / Local events
│   ├── models/
│   │   ├── __init__.py
│   │   └── event.py            # Event with scope field
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
│
├── requirements.txt
└── README.md
```

---

## Setup & Installation

### 1. Clone and create virtual environment

```bash
git clone <repo-url> chms
cd chms
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment variables

Create a `.env` file in the project root (never commit this):

```env
SECRET_KEY=your-very-secret-key-here
DEBUG=True

# Database
DB_NAME=chms_db
DB_USER=chms_user
DB_PASSWORD=chms_password
DB_HOST=localhost
DB_PORT=5432

# Invitation settings
INVITATION_EXPIRY_DAYS=7
FRONTEND_BASE_URL=http://localhost:3000

# Redis (for Celery)
REDIS_URL=redis://localhost:6379/0
```

Then update `chms/settings.py` to read from `.env` using `python-decouple`:

```python
from decouple import config

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME':     config('DB_NAME'),
        'USER':     config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST':     config('DB_HOST', default='localhost'),
        'PORT':     config('DB_PORT', default='5432'),
    }
}
```

### 3. Create the database

```bash
createdb chms_db
```

### 4. Run migrations

```bash
python manage.py makemigrations users organizations onboarding groups events
python manage.py migrate
```

### 5. Bootstrap the first Organisation

```bash
python manage.py bootstrap_org \
    --org-name  "My Church Network" \
    --org-slug  "my-church-network" \
    --org-country "South Africa" \
    --admin-email "admin@mychurch.org" \
    --admin-first "John" \
    --admin-last  "Doe"
```

### 6. Run the development server

```bash
python manage.py runserver
```

---

## The Hierarchy

```
Organization
    └── Region          (1 per national grouping)
            └── Province        (1 per state/city grouping)
                    └── Church          (local congregation)
                            ├── ChurchGroup (Home Group / Taskforce / Worship Team)
                            └── Event       (Local scope)
```

The hierarchy is **built organically through invitations** — no admin can skip levels.

---

## Role System

| Role | Scope | Can Invite |
|------|-------|-----------|
| `SUPER_ADMIN` | Organization-wide | APOSTLE, any role |
| `APOSTLE` | Organization-wide | ARCH_BISHOP, any lower |
| `ARCH_BISHOP` | Region | BISHOP |
| `BISHOP` | Province | CHURCH_ADMIN, PASTOR |
| `CHURCH_ADMIN` | Church | PASTOR, MINISTER, ELDER, DEACON, MEMBER |
| `PASTOR` | Church | ELDER, DEACON, MEMBER |
| `MINISTER` | Church | — |
| `ELDER` | Church | — |
| `DEACON` | Church | — |
| `MEMBER` | Church | — |

**Key rules (enforced in `SendInvitationSerializer`):**
- You cannot invite someone to a role equal to or above your own.
- Roles below APOSTLE must specify a `target_entity_id` (the Region/Province/Church UUID they are joining).

---

## Invitation & Onboarding Flow

```
SUPER_ADMIN
    │
    ├─ POST /api/onboarding/invitations/
    │      { email, role_proffered: "APOSTLE" }
    │
    └─► Apostle receives email with link:
            {FRONTEND_BASE_URL}/onboarding/accept/{token}/

        Frontend calls:
            GET /api/onboarding/validate/{token}/   ← pre-fills the form
            POST /api/onboarding/accept/
                { token, first_name, last_name, password }

        Apostle now invites Arch Bishops:
            POST /api/onboarding/invitations/
                { email, role_proffered: "ARCH_BISHOP",
                  target_entity_id: <region_uuid> }

        ... and so on down the hierarchy.
```

---

## API Reference

### Authentication

All protected endpoints require session or token auth.  
Add `rest_framework.authtoken` and `TokenAuthentication` for SPA/mobile use.

### Users

| Method | Endpoint | Role Required |
|--------|----------|--------------|
| GET | `/api/auth/users/` | Any authenticated |
| POST | `/api/auth/users/` | Admin role |
| GET | `/api/auth/users/{id}/` | Same org |
| PATCH | `/api/auth/users/{id}/` | Admin role |
| DELETE | `/api/auth/users/{id}/` | Admin role |

### Organizations

| Method | Endpoint | Role Required |
|--------|----------|--------------|
| GET | `/api/organizations/organizations/` | Any authenticated |
| PATCH | `/api/organizations/organizations/{id}/` | APOSTLE+ |
| GET/POST | `/api/organizations/regions/` | Any / ARCH_BISHOP+ |
| GET/POST | `/api/organizations/provinces/` | Any / BISHOP+ |
| GET/POST | `/api/organizations/churches/` | Any / CHURCH_ADMIN+ |

### Onboarding

| Method | Endpoint | Auth Required |
|--------|----------|--------------|
| POST | `/api/onboarding/invitations/` | Yes — Inviter role |
| GET | `/api/onboarding/invitations/` | Yes |
| DELETE | `/api/onboarding/invitations/{id}/` | Yes — revoke |
| GET | `/api/onboarding/validate/{token}/` | **No** — public |
| POST | `/api/onboarding/accept/` | **No** — public |

### Groups

| Method | Endpoint | Role Required |
|--------|----------|--------------|
| GET | `/api/groups/groups/` | Any authenticated |
| POST | `/api/groups/groups/` | CHURCH_ADMIN+ |
| POST | `/api/groups/memberships/` | CHURCH_ADMIN+ |

### Events

| Method | Endpoint | Role Required |
|--------|----------|--------------|
| GET | `/api/events/events/` | Any authenticated |
| POST | `/api/events/events/` | CHURCH_ADMIN+ (LOCAL), BISHOP+ (PROVINCIAL), APOSTLE+ (INTERNATIONAL) |

---

## Permissions Matrix

```
                        SUPER  APOS  ARCH  BISH  CH_AD PAST  MIN  ELDE  DEAC  MEMB
                        ADMIN  TLE   BISH  OP    MIN
Create Organization       ✅    ✅    ✗     ✗     ✗     ✗    ✗    ✗     ✗     ✗
Edit Organization         ✅    ✅    ✗     ✗     ✗     ✗    ✗    ✗     ✗     ✗
Create Region             ✅    ✅    ✅    ✗     ✗     ✗    ✗    ✗     ✗     ✗
Create Province           ✅    ✅    ✅    ✅    ✗     ✗    ✗    ✗     ✗     ✗
Create Church             ✅    ✅    ✅    ✅    ✅    ✗    ✗    ✗     ✗     ✗
Create Group              ✅    ✅    ✅    ✅    ✅    ✗    ✗    ✗     ✗     ✗
Create Local Event        ✅    ✅    ✅    ✅    ✅    ✗    ✗    ✗     ✗     ✗
Create Provincial Event   ✅    ✅    ✅    ✅    ✗     ✗    ✗    ✗     ✗     ✗
Create International Evt  ✅    ✅    ✗     ✗     ✗     ✗    ✗    ✗     ✗     ✗
Send Invitations          ✅    ✅    ✅    ✅    ✅    ✅   ✗    ✗     ✗     ✗
```

---

## Future Modules

### Finance Module
The scaffolding is already in place:
- `Organization.payment_metadata` — org-level payment provider config
- `Church.payment_metadata` — church-level giving configuration  
- `Event.budget` / `Event.finance_metadata` — event-level finance tracking

Next steps: add a `finance` app with `Pledge`, `Giving`, `Campaign` models referencing the Church FK already on every user's profile.

### Celery / Email
The invitation `create` view has a `# TODO` stub for:
```python
send_invitation_email.delay(invitation.id)
```
Add `onboarding/tasks.py` with a Celery task that sends the invitation email using Django's `send_mail` or a transactional provider (SendGrid, Mailgun).

### Taskforce ↔ Event Linking
Already wired — `ChurchGroup.events` is a M2M to `Event`.  
Query organizer groups for an event:
```python
event.organizer_groups.filter(group_type=GroupType.TASKFORCE)
```

---

## Running Tests

```bash
# Install test dependencies
pip install pytest pytest-django factory-boy coverage

# Run all tests
pytest

# With coverage report
coverage run -m pytest
coverage report -m
coverage html    # opens htmlcov/index.html
```

Test factories (to be built in `tests/factories.py`):
```python
import factory
from users.models import User
from organizations.models import Organization

class OrganizationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Organization
    name = factory.Sequence(lambda n: f"Church Network {n}")
    slug = factory.Sequence(lambda n: f"church-network-{n}")

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    email        = factory.Sequence(lambda n: f"user{n}@church.org")
    first_name   = "Test"
    last_name    = factory.Sequence(lambda n: f"User{n}")
    organization = factory.SubFactory(OrganizationFactory)
    role         = "MEMBER"
```
