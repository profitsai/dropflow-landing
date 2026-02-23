# DropFlow Landing Page & Dashboard

A Flask-powered marketing site and SaaS dashboard UI for DropFlow — the dropshipping automation engine for high-volume eBay sellers.

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # optional; or create .env manually
python app.py
```

Then visit **http://localhost:5000/**

## Environment Variables

Create a `.env` file in the project root. Example:

```env
SECRET_KEY=change-me-in-production
SQLALCHEMY_DATABASE_URI=sqlite:///dropflow.db
# Recommended: dedicated Fernet key for SupplierVault encryption
# Generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
VAULT_ENCRYPTION_KEY=replace-with-generated-fernet-key

# Email (Flask-Mail)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-smtp-username
MAIL_PASSWORD=your-smtp-password
MAIL_DEFAULT_SENDER=no-reply@yourdomain.com
```

If `VAULT_ENCRYPTION_KEY` is not set, `SECRET_KEY` is used as fallback key material.

Transactional emails (welcome + password reset) use Flask-Mail. If `MAIL_PASSWORD` is missing, the app falls back to mock mode and prints the full email payload to console instead of sending.

## Database & Migrations (Flask-Migrate / Alembic)

Initial setup:

```bash
export FLASK_APP=app.py
flask db init
flask db migrate -m "Initial schema"
flask db upgrade
```

After model changes:

```bash
flask db migrate -m "Describe change"
flask db upgrade
```

## Project Structure

```
├── app.py                  # Flask application, extension wiring, routes
├── models.py               # SQLAlchemy models + auth/encryption helpers
├── requirements.txt        # Python dependencies
├── static/
│   └── dashboard.jpg       # Dashboard screenshot for landing page
└── templates/
    ├── base.html            # Marketing pages base (nav, footer, Tailwind CDN, Alpine.js)
    ├── dashboard_base.html  # Dashboard pages base (sidebar, toast system)
    ├── index.html           # Landing page (hero, features, scraper spotlight, testimonials, FAQ)
    ├── pricing.html         # Pricing tiers ($29 Stealth / $79 Pro)
    ├── login.html           # Login (Google SSO + email)
    ├── signup.html          # Signup (Google SSO + email, $1 trial CTA)
    ├── dashboard.html       # Dashboard (stats, charts, date picker)
    ├── products.html        # Product catalog (status badges, hover actions, skeleton loading)
    ├── orders.html          # Order management (fulfillment triage, status dropdown, hover actions)
    ├── import.html          # Import console (Amazon/AliExpress toggle, bulk URLs, drafts table)
    ├── scraper.html         # Store scraper (3-platform toggle, credits wallet, jobs table)
    └── settings.html        # Settings (5 tabs: Pricing, Orders, Lister, Buyer Accounts, Stores)
```

## Routes

| Route | Template | Description |
|-------|----------|-------------|
| `/` | `index.html` | Marketing landing page |
| `/pricing` | `pricing.html` | Pricing tiers |
| `/login` | `login.html` | Login page |
| `/signup` | `signup.html` | Signup page (also `/register`) |
| `/dashboard` | `dashboard.html` | Main dashboard |
| `/products` | `products.html` | Product catalog |
| `/orders` | `orders.html` | Order management |
| `/import` | `import.html` | Import console |
| `/scraper` | `scraper.html` | Store scraper |
| `/settings` | `settings.html` | App settings |

## Auth Smoke Test (manual)

After `flask db upgrade` and `python app.py`, verify auth quickly:

1. Open `http://localhost:5000/dashboard` while logged out → should redirect to `/login`.
2. Go to `http://localhost:5000/signup` and create a user with email/password.
3. You should be redirected to `/dashboard` as a logged-in user.
4. In a new private/incognito window, log in via `http://localhost:5000/login` using the same credentials.
5. (Optional logout check) run this in your browser console while logged in:
   ```js
   fetch('/logout', { method: 'POST' }).then(() => location.href = '/dashboard')
   ```
   You should be redirected back to `/login`.

## Tech Stack

- **Backend:** Flask + Flask-SQLAlchemy + Flask-Login + Flask-Migrate
- **Security:** Werkzeug password hashing + Fernet encryption for SupplierVault secrets
- **Config:** python-dotenv
- **CSS:** Tailwind CSS v3 (CDN)
- **Interactivity:** Alpine.js (CDN) — all UI state is client-side
- **Charts:** ApexCharts (dashboard)
- **Date Picker:** Flatpickr (dashboard)

## Notes for Developers

- All templates use Jinja2 `{% extends %}` / `{% block %}` inheritance
- Marketing pages extend `base.html` — includes nav, footer, scroll animations
- Dashboard pages extend `dashboard_base.html` — includes sidebar, Alpine.js toast store
- Internal links use Flask `url_for()` or relative paths (`/dashboard`, `/products`, etc.)
- Database schema now includes: `User`, `EbayStore`, `SupplierVault`, `Product`, `Order`
- `[x-cloak]` CSS rule is included for clean Alpine.js transitions
