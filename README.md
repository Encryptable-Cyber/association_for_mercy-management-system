# Association for Mercy Management Platform

[![Django](https://img.shields.io/badge/Django-6.0-092E20?logo=django)](https://www.djangoproject.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-7-DC382D?logo=redis)](https://redis.io/)
[![Docker](https://img.shields.io/badge/Docker-✓-2496ED?logo=docker)](https://www.docker.com/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5-7952B3?logo=bootstrap)](https://getbootstrap.com/)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python)](https://www.python.org/)

A **secure, full-stack NGO management platform** designed for the Association for Mercy — a Cameroonian humanitarian organization. The platform digitizes core operations including beneficiary tracking, donation management, membership onboarding, program oversight, and administrative governance with **enterprise-grade cybersecurity** at every layer.

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [System Architecture](#system-architecture)
- [Security Mechanisms](#security-mechanisms)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [User Roles & Permissions](#user-roles--permissions)
- [Workflows](#workflows)
- [Reporting System](#reporting-system)
- [Internationalization](#internationalization)
- [Deployment](#deployment)
- [Screenshots](#screenshots)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

The Association for Mercy Management Platform transforms manual humanitarian operations into secure digital workflows. It serves both **public visitors** (donors, membership applicants) and **internal staff** (administrators, case workers) through a unified, bilingual interface.

### Problems Solved

| Before | After |
|--------|-------|
| Fragmented beneficiary records across paper files | Centralized database with status tracking and case management |
| Manual donation tracking without receipts | Auto-generated receipts with multi-currency and program linkage |
| Informal membership processing | Structured workflow: application → documents → review → invitation → OTP → activation |
| No reporting capabilities | 5 report types with PDF, Excel, and Print export |
| No access controls | Three-role RBAC (Super Admin, Admin, Staff) with 403 enforcement |
| No audit trail | Comprehensive audit logging of all sensitive actions |

---

## Key Features

### Public Portal

- **Landing Page** — Hero section, impact statistics, "What We Do" cards, activity gallery, calls-to-action
- **Donation Intent Form** — Multi-currency (XAF, USD, EUR, etc.), frequency options, nationality with flag selection, phone code picker, preferred contact method
- **Membership Application** — Comprehensive profiling: personal, professional, education, 25 areas of interest with checkbox grid, motivation, contribution
- **Language Switcher** — English/Français toggle on all pages using Django's i18n framework

### Membership Onboarding

- **Document Upload** — PDF, JPG, PNG support with file type/size validation (5MB max)
- **Admin Review Interface** — View applications, supporting documents, add notes, approve/reject
- **Invitation-Based Account Creation** — UUID tokens, 72-hour expiry, single-use enforcement
- **Profile Picture Upload** — Image validation during signup
- **OTP Verification** — 6-digit code sent to email, SHA-256 hashed, 10-minute expiry, 3 attempts max

### Internal Management

- **Beneficiary Management** — Full CRUD with status tracking (Active, Inactive, Urgent), search, filtering
- **Case Tracking** — Create cases per beneficiary, assign priorities (Low to Urgent), link to programs
- **Intervention Recording** — Timestamped actions with performer attribution
- **Program Management** — Lifecycle tracking (Planned, Active, Completed, Cancelled), budget oversight
- **Donation Management** — Auto-generated receipt numbers (RCP-XXXXXX), payment method tracking, program linkage
- **Activity Management** — Admin-managed images for landing page showcase

### Administration

- **User Management Dashboard** — Search, filter by role/status, activate/deactivate, promote/demote
- **Super Admin Protection** — Cannot deactivate or demote the last active Super Admin
- **Password Reset** — Super Admin generates secure link → user sets password → OTP verified → saved
- **Audit Logging** — 12 action types tracked with user, timestamp, description, IP address

### Reporting

- **5 Report Types** — Beneficiaries, Donations, Programs, Memberships, Users
- **Export Formats** — PDF (ReportLab with branded headers), Excel (openpyxl with styled spreadsheets), Browser Print
- **Multi-Criteria Filtering** — By year, month, status, program, payment method
- **Export Audit Logging** — Who exported what, when, with what filters

---

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Backend** | Django 6.0 | Web framework, ORM, auth, admin |
| **Language** | Python 3.12 | Core programming language |
| **Database** | PostgreSQL 16 | Production relational database |
| **Cache/Sessions** | Redis 7 | In-memory session storage, caching |
| **Frontend** | Bootstrap 5 | Responsive CSS framework |
| **Icons** | Bootstrap Icons | UI iconography |
| **Fonts** | Google Fonts (Inter) | Typography |
| **PDF Export** | ReportLab | Professional PDF generation |
| **Excel Export** | openpyxl | Structured spreadsheet creation |
| **Containerization** | Docker + Docker Compose | Consistent environments |
| **Email** | Gmail SMTP | OTP and notification delivery |
| **i18n** | Django gettext | English/French translations |

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CLIENT BROWSER                            │
│              (Bootstrap 5 + Django Templates)                │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                  DJANGO APPLICATION                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────────┐  │
│  │   Views  │  │  Forms   │  │  Security Middleware      │  │
│  │  (Logic) │  │(Validat) │  │  (CSRF, CSP, RBAC, Rate) │  │
│  └────┬─────┘  └────┬─────┘  └──────────┬───────────────┘  │
│       │              │                   │                   │
│  ┌────▼──────────────▼───────────────────▼───────────────┐  │
│  │                 Django ORM                             │  │
│  └──────────────────────┬────────────────────────────────┘  │
└─────────────────────────┼───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                    DATA LAYER                                 │
│  ┌──────────────────┐  ┌──────────────────┐                 │
│  │   PostgreSQL 16  │  │    Redis 7       │                 │
│  └──────────────────┘  └──────────────────┘                 │
└─────────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                 DOCKER INFRASTRUCTURE                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │  Django  │  │PostgreSQL│  │  Redis   │                  │
│  │Container │  │Container │  │Container │                  │
│  │  :8000   │  │  :5432   │  │  :6379   │                  │
│  └──────────┘  └──────────┘  └──────────┘                  │
│              Internal Network (Bridge)                       │
└─────────────────────────────────────────────────────────────┘
```

### Django Apps

| App | Models | Templates | Purpose |
|-----|--------|-----------|---------|
| `users` | User, MembershipApplication, MembershipDocument, OTP, AuditLog | 10 | Auth, membership, admin |
| `beneficiaries` | Beneficiary, Case, Intervention | 6 | Beneficiary & case management |
| `programs` | Program | 3 | Program lifecycle |
| `donations` | Donation, DonationIntent | 6 | Donation tracking & intents |
| `core` | Activity, ExportLog | 3 | Dashboard, landing, reports |

### Database Schema (13 Tables)

| Table | Key Fields |
|-------|-----------|
| `users_user` | email, role (super_admin/admin/staff), is_active, profile_picture |
| `users_membershipapplication` | Full applicant profile, status, signup_token (UUID) |
| `users_membershipdocument` | document (FileField), document_type |
| `users_otp` | otp_hash (SHA-256), purpose, expires_at, used |
| `users_auditlog` | user, action, description, target_user, ip_address |
| `beneficiaries_beneficiary` | name, status (active/inactive/urgent) |
| `beneficiaries_case` | beneficiary, priority, status, program |
| `beneficiaries_intervention` | case, description, performed_by |
| `programs_program` | name, budget, status (planned/active/completed) |
| `donations_donation` | receipt_number (unique), amount, currency |
| `donations_donationintent` | donation_type, currency, frequency |
| `core_activity` | title, image, is_active |
| `core_exportlog` | user, report_type, export_type, filters_applied |

---

## Security Mechanisms

### Defense in Depth

| Layer | Mechanisms |
|-------|-----------|
| **Network** | Docker internal network, PostgreSQL not exposed, Redis password-protected |
| **Application** | CSRF tokens, CSP/X-Frame-Options/HSTS headers, rate limiting |
| **Authentication** | Email login, PBKDF2+SHA-256 hashing, OTP verification, RBAC decorators |
| **Data** | Django ORM (anti-SQL injection), file validation, OTP SHA-256 hashed |
| **Accountability** | Audit logging (12 action types), export logging, IP tracking |

### Security Checklist (18 Mechanisms)

| # | Mechanism | Implementation |
|---|-----------|---------------|
| 1 | Custom User Model | Email-based login, no username enumeration |
| 2 | Password Hashing | PBKDF2 with SHA-256 (Django default) |
| 3 | OTP Verification | 6-digit, SHA-256 hashed, 10-min expiry, 3 attempts |
| 4 | Role-Based Access Control | 3 roles + custom decorators returning 403 |
| 5 | Last Admin Protection | Cannot deactivate/demote last Super Admin |
| 6 | CSRF Protection | `{% csrf_token %}` on all forms, global middleware |
| 7 | Security Headers | CSP, X-Frame-Options (DENY), X-Content-Type-Options (nosniff) |
| 8 | Rate Limiting | Custom decorator, 5 requests/5 minutes on public forms |
| 9 | File Type Validation | PDF, JPG, JPEG, PNG only for documents |
| 10 | File Size Limits | 5MB (documents), 2MB (profile pictures) |
| 11 | SQL Injection Prevention | Django ORM exclusively — no raw SQL |
| 12 | XSS Prevention | Django template auto-escaping |
| 13 | HTTP-Only Cookies | Session cookies inaccessible to JavaScript |
| 14 | SameSite Cookies | `SESSION_COOKIE_SAMESITE = 'Lax'` |
| 15 | Session Expiry | 24 hours with refresh on activity |
| 16 | Docker Non-Root User | Application runs as restricted `mercy` user |
| 17 | Environment Variables | Secrets in `.env`, never in code or images |
| 18 | Audit Logging | All sensitive actions tracked with user, IP, timestamp |

---

## Project Structure

```
association_for_mercy/
├── beneficiaries/          # Beneficiary & Case management
│   ├── forms/              # Django Forms
│   ├── migrations/         # Database migrations
│   ├── models.py           # Beneficiary, Case, Intervention
│   ├── views.py            # CRUD + report views
│   └── urls.py             # URL routing
├── config/                 # Django project settings
│   ├── settings.py         # All configuration
│   ├── urls.py             # Root URL configuration
│   └── wsgi.py             # WSGI entry point
├── core/                   # Shared logic & security
│   ├── models.py           # Activity, ExportLog
│   ├── permissions.py      # RBAC decorators
│   ├── reports.py          # PDF/Excel generation
│   ├── security.py         # Security middleware + rate limiting
│   ├── utils.py            # Shared utilities (IP extraction)
│   ├── countries.py        # Country data with flags & phone codes
│   └── email.py            # Custom email backend
├── donations/              # Donation management
│   ├── forms/              # Donation + DonationIntent forms
│   ├── models.py           # Donation, DonationIntent
│   ├── views.py            # CRUD + review + report views
│   └── urls.py
├── locale/                 # Translations
│   └── fr/LC_MESSAGES/
│       ├── django.po       # French translations
│       └── django.mo       # Compiled translations
├── media/                  # User-uploaded files
├── programs/               # Program management
│   ├── models.py           # Program
│   ├── views.py            # CRUD + report views
│   └── urls.py
├── static/                 # Static assets
│   ├── css/                # Stylesheets (app.css, public.css, forms.css)
│   ├── js/                 # JavaScript (phone-picker.js)
│   └── images/             # Logo, favicon
├── templates/              # HTML templates
│   ├── 403.html, 404.html, 500.html  # Custom error pages
│   ├── beneficiaries/      # 6 templates
│   ├── core/               # base.html, dashboard.html, landing.html, base_public.html
│   ├── donations/          # 6 templates
│   ├── programs/           # 3 templates
│   ├── registration/       # login + password reset templates
│   └── users/              # 10 templates
├── users/                  # Authentication & Membership
│   ├── forms/              # Membership + Document forms
│   ├── models.py           # User, MembershipApplication, OTP, AuditLog
│   ├── views.py            # Auth, membership, admin, OTP, audit views
│   └── urls.py
├── .env.example            # Environment variables template (safe to commit)
├── .dockerignore           # Docker build exclusions
├── .gitignore              # Git ignore rules
├── docker-compose.yml      # Docker Compose (3 services)
├── dockerfile              # Docker image definition
├── entrypoint.sh           # Container startup script
├── requirements.txt        # Python dependencies
├── manage.py               # Django management script
└── README.md               # This file
```

---

## Getting Started

### Prerequisites

- **Docker Desktop** installed and running
- **Git** installed

### Quick Start (Docker)

```bash
# Clone the repository
git clone https://github.com/Encryptable-Cyber/association_for_mercy-management-system.git
cd association_for_mercy-management-system

# Copy environment variables template
cp .env.example .env
# Edit .env with your settings (especially EMAIL_HOST_USER and EMAIL_HOST_PASSWORD)

# Start all services
docker compose up -d

# Run migrations (handled automatically by entrypoint.sh)
docker compose exec web python manage.py migrate

# Create superuser
docker compose exec web python manage.py createsuperuser

# Promote to Super Admin
docker compose exec web python manage.py shell
>>> from users.models import User
>>> user = User.objects.get(email='your-email@example.com')
>>> user.role = 'super_admin'
>>> user.save()
>>> exit()

# Open the application
# http://127.0.0.1:8000/
```

### Manual Setup (Without Docker)

```bash
# Clone and set up virtual environment
git clone https://github.com/Encryptable-Cyber/association_for_mercy-management-system.git
cd association_for_mercy-management-system
python -m venv venv
source venv/Scripts/activate  # Windows
# source venv/bin/activate     # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure database (SQLite for development)
# Edit config/settings.py or set environment variables

# Run migrations
python manage.py migrate
python manage.py createsuperuser

# Start server
python manage.py runserver
# http://127.0.0.1:8000/
```

---

## User Roles & Permissions

| Feature | Public | Staff | Admin | Super Admin |
|---------|--------|-------|-------|-------------|
| Landing Page | ✅ | ✅ | ✅ | ✅ |
| Donation Intent Form | ✅ | ✅ | ✅ | ✅ |
| Membership Application | ✅ | ✅ | ✅ | ✅ |
| Document Upload | ✅ | ✅ | ✅ | ✅ |
| Dashboard | ❌ | ✅ | ✅ | ✅ |
| Beneficiary CRUD | ❌ | ✅ | ✅ | ✅ |
| Program Management | ❌ | ✅ | ✅ | ✅ |
| Record Donations | ❌ | ✅ | ✅ | ✅ |
| Export Reports | ❌ | ✅ | ✅ | ✅ |
| Review Donation Intents | ❌ | ❌ | ✅ | ✅ |
| Review Membership Apps | ❌ | ❌ | ✅ | ✅ |
| View Audit Log | ❌ | ❌ | ❌ | ✅ |
| User Management | ❌ | ❌ | ❌ | ✅ |
| Change Roles | ❌ | ❌ | ❌ | ✅ |

---

## Workflows

### Membership Onboarding

```
Public User → Submit Application → Upload Documents (ID, CV, Certificates)
    → Admin Reviews → Approves → UUID Token Generated
    → Applicant Receives Invitation Link → Creates Account
    → Uploads Profile Picture → OTP Emailed → OTP Verified → Account Active
```

### Donation Flow

```
Public User → Submit Donation Intent → Admin Reviews
Staff → Record Donation → Auto-Generate Receipt (RCP-XXXXXX) → Link to Program
    → Export Report (PDF/Excel/Print)
```

### Authentication Flow

```
Account Activation: Signup → OTP Generated → OTP Emailed → OTP Verified → Active
Password Reset: Super Admin → Generate Link → User Sets Password → OTP Verified → Saved
Login: Email + Password → Session Created → Role-Based Dashboard
```

---

## Reporting System

### Available Reports

| Report | URL | Filters | Access |
|--------|-----|---------|--------|
| Beneficiaries | `/beneficiaries/report/` | Status, Year, Month, Search | Staff+ |
| Donations | `/donations/report/` | Method, Program, Year, Month, Search | Staff+ |
| Programs | `/programs/report/` | Status, Year, Month, Search | Staff+ |
| Memberships | `/memberships/report/` | Status, Year, Month, Search | Admin+ |
| Users | `/users/report/` | Role, Status, Year, Month, Search | Super Admin |

### Export Formats

- **PDF** — ReportLab with branded headers, styled tables, professional pagination
- **Excel** — openpyxl with styled headers, auto-adjusted columns, merged title rows
- **Print** — Browser print with CSS hiding navigation, sidebar, and buttons

All exports are **audit logged** (user, report type, export format, filters, timestamp, IP).

---

## Internationalization

The platform supports **English** and **French** using Django's i18n framework.

- **250+ translated strings** in `locale/fr/LC_MESSAGES/django.po`
- **Language switcher** (EN/FR buttons) on all pages — public and internal
- **Compiled translations** (`.mo` files) ready for production use
- All user-facing text uses `{% trans %}` template tags

### Adding New Languages

```bash
docker compose exec web python manage.py makemessages -l es  # Spanish
# Edit locale/es/LC_MESSAGES/django.po
docker compose exec web python manage.py compilemessages -l es
```

---

## Deployment

### Production Checklist

- [ ] Set `DEBUG=False` in `.env`
- [ ] Generate new `SECRET_KEY` (`python -c "import secrets; print(secrets.token_urlsafe(50))"`)
- [ ] Set `ALLOWED_HOSTS` to your domain
- [ ] Enable `SECURE_SSL_REDIRECT=True`
- [ ] Enable `SESSION_COOKIE_SECURE=True`
- [ ] Enable `CSRF_COOKIE_SECURE=True`
- [ ] Set `SECURE_HSTS_SECONDS=31536000`
- [ ] Use Gunicorn instead of `runserver` (update Dockerfile CMD)
- [ ] Add Nginx reverse proxy for static/media files
- [ ] Use managed PostgreSQL (AWS RDS, DigitalOcean, etc.)
- [ ] Set up real email backend (Gmail SMTP or SendGrid)
- [ ] Configure automated backups for database and media

### Docker Deployment

```bash
# Build for production
docker compose build

# Run in detached mode
docker compose up -d

# View logs
docker compose logs -f web
```

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## License

This project is licensed under the MIT License.

---

## Acknowledgments

- [Django](https://www.djangoproject.com/) — The web framework for perfectionists with deadlines
- [Bootstrap](https://getbootstrap.com/) — Frontend component library
- [ReportLab](https://www.reportlab.com/) — PDF generation
- [openpyxl](https://openpyxl.readthedocs.io/) — Excel file handling
- [Docker](https://www.docker.com/) — Containerization platform
- [PostgreSQL](https://www.postgresql.org/) — Database
- [Redis](https://redis.io/) — In-memory data store

---

**Built with ❤️ for the Association for Mercy | Compassion · Assistance · Integrity**
