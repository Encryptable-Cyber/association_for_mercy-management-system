# Association for Mercy Platform

A secure, full-stack NGO management system built with Django. The platform enables organizations to manage beneficiaries, programs, donations, cases, and membership applications with role-based access control, comprehensive reporting, and multi-language support.

---

## 🚀 Features

### Core Management
- **Beneficiary Management** — Track individuals receiving assistance with status tracking (Active, Inactive, Urgent)
- **Program Management** — Manage NGO initiatives with budgets, timelines, and statuses
- **Case Tracking** — Create cases for beneficiaries, track interventions and resolutions
- **Donation Tracking** — Record financial contributions with receipt generation and multi-currency support
- **Activity Showcase** — Display NGO activities with images on the public landing page

### Public Features
- **Donation Intent Form** — Public users can submit donation requests with multi-currency options
- **Membership Application** — Comprehensive application form with professional profiling
- **Secure Signup** — Approved applicants receive unique signup tokens via admin review

### Admin Features
- **Review Dashboard** — Review donation intents and membership applications
- **User Management** — Super Admin can promote/demote users, deactivate accounts
- **Last Super Admin Protection** — System prevents accidental lockout

### Reporting (PDF, Excel, Print)
- Beneficiary reports with year/month/status filters
- Donation reports with program/method/year/month filters
- Program reports with status/year/month filters
- Membership application reports
- User management reports (Super Admin only)
- Export audit logging for accountability

### Security
- **Role-Based Access Control** — Super Admin, Admin, Staff roles with granular permissions
- **CSRF Protection** — All forms protected against cross-site request forgery
- **Security Headers** — CSP, X-Frame-Options, HSTS, and more
- **Rate Limiting** — Public forms protected against abuse
- **Audit Logging** — Export actions tracked with user, timestamp, and IP
- **Soft Deactivation** — Users are deactivated, never deleted (preserves audit trails)
- **Secure Authentication** — Email-based login, PBKDF2 password hashing, HTTP-only cookies

### Internationalization (i18n)
- **English & French** — Full translation support with language switcher
- Django's native i18n framework with compiled `.po`/`.mo` files

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Django 6.0 |
| Database | SQLite (development) |
| Frontend | Bootstrap 5, Bootstrap Icons |
| Fonts | Google Fonts (Inter) |
| PDF Export | ReportLab |
| Excel Export | openpyxl |
| i18n | Django gettext |
| Image Handling | Pillow |

---

## 📁 Project Structure

```
association_for_mercy/
├── beneficiaries/          # Beneficiary & Case management
│   ├── forms/
│   ├── migrations/
│   ├── admin.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── config/                 # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── core/                   # Shared logic, dashboard, reports, security
│   ├── migrations/
│   ├── admin.py
│   ├── models.py
│   ├── permissions.py
│   ├── reports.py
│   ├── security.py
│   ├── urls.py
│   └── views.py
├── donations/              # Donations & donation intents
│   ├── forms/
│   ├── migrations/
│   ├── admin.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── locale/                 # Translation files (EN/FR)
│   └── fr/LC_MESSAGES/
├── programs/               # Program management
│   ├── forms/
│   ├── migrations/
│   ├── admin.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── static/                 # Static files (logo, etc.)
│   └── images/
├── templates/              # HTML templates
│   ├── beneficiaries/
│   ├── core/               # base.html, dashboard.html, landing.html
│   ├── donations/
│   ├── programs/
│   ├── registration/       # login.html
│   └── users/              # membership, user management
├── users/                  # Custom User model, auth, membership
│   ├── forms/
│   ├── migrations/
│   ├── admin.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── media/                  # Uploaded files (activities)
├── manage.py
└── README.md
```

---

## 🔐 Role-Based Access Matrix

| Feature | Public | Staff | Admin | Super Admin |
|---------|--------|-------|-------|-------------|
| Landing Page | ✅ | ✅ | ✅ | ✅ |
| Dashboard | ❌ | ✅ | ✅ | ✅ |
| Beneficiaries CRUD | ❌ | ✅ | ✅ | ✅ |
| Programs CRUD | ❌ | ✅ | ✅ | ✅ |
| Cases & Interventions | ❌ | ✅ | ✅ | ✅ |
| Record Donations | ❌ | ✅ | ✅ | ✅ |
| Submit Donation Intent | ✅ | ✅ | ✅ | ✅ |
| Apply for Membership | ✅ | ✅ | ✅ | ✅ |
| Review Donation Intents | ❌ | ❌ | ✅ | ✅ |
| Review Membership Apps | ❌ | ❌ | ✅ | ✅ |
| User Management | ❌ | ❌ | ❌ | ✅ |
| Export Reports | ❌ | ✅ | ✅ | ✅ |
| User Reports | ❌ | ❌ | ❌ | ✅ |

---

## 🚦 Getting Started

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/Encryptable-Cyber/association_for_mercy-management-system.git
cd association-for-mercy
```

### 2. Create and Activate Virtual Environment

**Windows (Git Bash):**
```bash
python -m venv venv
source venv/Scripts/activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install django reportlab openpyxl Pillow
```

### 4. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Super User

```bash
python manage.py createsuperuser
```

Follow the prompts:
- Email: `admin@mercy.org`
- Username: `admin`
- First Name: `Admin`
- Last Name: `User`
- Password: (choose a strong password)

After creation, you'll need to promote this user to Super Admin via the Django shell:

```bash
python manage.py shell
```

```python
from users.models import User
user = User.objects.get(email='admin@mercy.org')
user.role = 'super_admin'
user.save()
exit()
```

### 6. Start the Development Server

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` to access the landing page.

### 7. Create Translation Files (Optional)

**On Windows, install GNU gettext first:**
Download from: https://github.com/mlocati/gettext-iconv-windows/releases

Then:
```bash
python manage.py makemessages -l fr
# Edit locale/fr/LC_MESSAGES/django.po with French translations
python manage.py compilemessages -l fr
```

---

## 🔧 Configuration

### Key Settings (`config/settings.py`)

| Setting | Development | Production |
|---------|-------------|------------|
| `DEBUG` | `True` | `False` |
| `SECRET_KEY` | Default | Strong random value |
| `ALLOWED_HOSTS` | `[]` | `['yourdomain.com']` |
| `SECURE_SSL_REDIRECT` | `False` | `True` |
| `SESSION_COOKIE_SECURE` | `False` | `True` |
| `CSRF_COOKIE_SECURE` | `False` | `True` |

---

## 📊 Reports

All reports support three export formats and multiple filters:

| Report | URL | Filters | Access |
|--------|-----|---------|--------|
| Beneficiaries | `/beneficiaries/report/` | Status, Year, Month, Search | Staff+ |
| Donations | `/donations/report/` | Method, Program, Year, Month, Search | Staff+ |
| Programs | `/programs/report/` | Status, Year, Month, Search | Staff+ |
| Membership Apps | `/memberships/report/` | Status, Year, Month, Search | Admin+ |
| Users | `/users/report/` | Role, Status, Year, Month, Search | Super Admin |

---

## 🔒 Security Features

### Implemented Protections

- **Clickjacking Protection:** `X-Frame-Options: DENY`
- **XSS Protection:** Content-Security-Policy headers
- **MIME Sniffing Prevention:** `X-Content-Type-Options: nosniff`
- **CSRF Protection:** All POST forms include `{% csrf_token %}`
- **SQL Injection Prevention:** Django ORM for all queries
- **Password Security:** PBKDF2 with SHA256 hashing
- **Session Security:** HTTP-only, SameSite cookies
- **Rate Limiting:** Public forms limited to 5 requests per 5 minutes
- **Audit Logging:** All data exports logged with user, type, timestamp, and IP

### Deployment Checklist

Before deploying to production:

- [ ] Set `DEBUG = False`
- [ ] Generate a new `SECRET_KEY`
- [ ] Set `ALLOWED_HOSTS` to your domain
- [ ] Set `SECURE_SSL_REDIRECT = True`
- [ ] Set `SESSION_COOKIE_SECURE = True`
- [ ] Set `CSRF_COOKIE_SECURE = True`
- [ ] Set `SECURE_HSTS_SECONDS = 31536000`
- [ ] Switch to PostgreSQL or MySQL
- [ ] Configure email backend for notifications
- [ ] Set up a proper static/media file server
- [ ] Enable HTTPS with a valid SSL certificate

---

## 🧪 Testing

### Test Flows

1. **Public Visitor:** Landing page → Switch to French → Submit donation intent → Apply for membership
2. **Admin Login:** Staff login → Review donation intents → Review membership applications → Approve application
3. **New Staff Signup:** Open signup link → Create password → Log in → Access dashboard
4. **Beneficiary Management:** Add beneficiary → Create case → Add intervention
5. **Donation Recording:** Record donation → Generate receipt
6. **Program Management:** Create program → Assign cases → Track donations
7. **Reports:** Filter by year/month → Export PDF → Export Excel → Print
8. **User Management:** Promote to Admin → Demote to Staff → Deactivate account → Reactivate

---

## 🐛 Troubleshooting

### Server Won't Start
```bash
# Clear Python cache
find . -type d -name "__pycache__" -exec rm -rf {} +
# Try without auto-reloader
python manage.py runserver --noreload
```

### Pillow Not Detected
```bash
pip uninstall Pillow -y
pip install Pillow --force-reinstall --no-cache-dir
```

### Translations Not Working
```bash
python manage.py compilemessages -l fr
# Restart server completely
```

### gettext Not Found (Windows)
Download from: https://github.com/mlocati/gettext-iconv-windows/releases
Add to PATH: `export PATH="/c/Program Files/gettext-iconv/bin:$PATH"`

---

## 📄 License

This project is licensed under the MIT License.

---

## 🙏 Acknowledgments

- [Django](https://www.djangoproject.com/) — The web framework for perfectionists with deadlines
- [Bootstrap](https://getbootstrap.com/) — Frontend component library
- [Bootstrap Icons](https://icons.getbootstrap.com/) — Free, high quality icons
- [ReportLab](https://www.reportlab.com/) — PDF generation library
- [openpyxl](https://openpyxl.readthedocs.io/) — Excel file handling
- [Google Fonts](https://fonts.google.com/) — Inter font family
- [gettext-iconv-windows](https://github.com/mlocati/gettext-iconv-windows) — GNU gettext for Windows

---

**Built with ❤️ for the Association for Mercy**