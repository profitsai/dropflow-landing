# DropFlow — Technical Manifesto & Handoff Brief

Enterprise-grade **eBay dropshipping automation** with an **API Cloud engine**.

This repo (`dropflow-landing`) contains the Flask app + Jinja2/Tailwind UI shell, authentication, database schema, migrations, and transactional email templates. It is designed to be handed off to a human developer to wire in the real scraper/automation engine and production infrastructure.

---

## Handoff Checklist (do this first)

1) **Create and activate a venv**
```bash
python -m venv .venv
source .venv/bin/activate
```

2) **Install dependencies**
```bash
pip install -r requirements.txt
```

3) **Create `.env` from the template**
```bash
cp .env.example .env
```
- Set `SECRET_KEY`
- Generate and set **`VAULT_ENCRYPTION_KEY`** (Fernet)
- (Optional) configure SMTP `MAIL_*` (otherwise emails print to console)

4) **Run DB migrations**
```bash
export FLASK_APP=app.py
flask db upgrade
```

5) **Run the app**
```bash
python app.py
```
Visit: http://127.0.0.1:5000

6) **Smoke test auth + reset flow**
- Visit `/dashboard` while logged out → should redirect to `/login`
- Create user at `/signup` → redirected to `/dashboard`
- Trigger reset at `/forgot-password` → check console mock email and open `/reset-password/<token>`

7) **Next implementation targets (highest ROI)**
- Implement `POST /api/scrape` and queue jobs (Celery/RQ recommended)
- Replace placeholder rows in `/products` and `/orders` with SQLAlchemy + Jinja loops
- When business keys are ready: Stripe checkout + webhooks to set `active_plan` + `sku_limit`

---

## Project Overview

DropFlow is an enterprise-grade dropshipping automation platform for high-volume eBay sellers.

Core premise:
- Users import products from **Amazon / AliExpress / eBay competitor stores**.
- DropFlow’s **API Cloud engine** monitors inventory + price changes and executes **fully automated fulfillment**.
- The UI is designed to make the system feel “hands-free”, with dashboards, inventory/order views, and an AI Scraper Engine.

---

## Tech Stack

**Backend**
- Flask
- Flask-SQLAlchemy
- Flask-Login
- Flask-Migrate (Alembic)
- Flask-Mail (transactional emails; mock prints to console when SMTP not configured)
- python-dotenv
- itsdangerous (timed reset tokens)

**Frontend (Jinja templates)**
- TailwindCSS (CDN)
- Alpine.js (CDN)

---

## Architecture & Security

### Layout split: Marketing vs App

We intentionally split the template foundations to keep the codebase clean:
- `templates/layouts/base_marketing.html` — public site (landing/pricing/legal)
- `templates/layouts/base_app.html` — authenticated dashboard shell (sidebar + app pages)

Wrapper templates remain for compatibility:
- `templates/base.html` → extends marketing base
- `templates/dashboard_base.html` → extends app base

### SupplierVault encryption (CRITICAL)

Supplier credentials **MUST NOT** be stored in plaintext.

- The `SupplierVault.encrypted_password` column stores encrypted bytes as text.
- Encryption is implemented in `models.py` using `cryptography.fernet.Fernet`.
- The cipher key is sourced from environment:
  - `VAULT_ENCRYPTION_KEY` (preferred)
  - otherwise `SECRET_KEY` is used as fallback material.

**Human developer requirements**
- Treat `VAULT_ENCRYPTION_KEY` like a production secret.
- Rotate carefully: changing the key breaks decryption of existing rows.
- Use a dedicated Fernet key in production:
  ```bash
  python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
  ```

---

## Operational Logic (Product Matching & Fulfillment)

The UI copy references an **“Advanced Product Matching System”**.

Design intent:
- This system exists to support **fully automated fulfillment**.
- If margins and stock are valid, the backend should **not pause** for manual approval.
- Manual review should only occur when safety rules trigger (OOS, price cap exceeded, missing credentials, etc.).

---

## Status Report (What’s Built)

### UI (complete shell)
**Marketing**
- Landing: `/`
- Pricing: `/pricing`
- Legal: `/terms`, `/privacy`, `/refund`

**App (authenticated)**
- Dashboard: `/dashboard`
- Scraper Engine: `/scraper`
- Inventory list: `/products` (static placeholder table)
- Orders list: `/orders` (static placeholder table)
- Product detail: `/products/<product_id>`
- Order detail: `/orders/<order_id>`
- Settings & Billing: `/settings` (Alpine tab system)
- Stripe return pages: `/upgrade-success`, `/upgrade-cancelled`

### Secure Auth
- Login / Signup (Flask-Login sessions)
- Password hashing: Werkzeug
- Timed reset tokens (1 hour) using itsdangerous:
  - `/forgot-password`
  - `/reset-password/<token>` (GET + POST)

### Transactional Email Templates
Located in `templates/emails/`:
- `welcome.html`
- `reset_password.html`
- `order_error.html`
- `first_sale.html`

Email sending behavior:
- If SMTP credentials are missing (`MAIL_PASSWORD` empty), the app prints a mock email to console.
- If SMTP credentials exist, Flask-Mail sends real emails.

### Database + Migrations
- SQLAlchemy models: `models.py` (User, EbayStore, SupplierVault, Product, Order)
- Flask-Migrate/Alembic: `migrations/`

---

## Human Developer To‑Do List

### 1) Scraper integration (core)
Wire the real headless scraper/AI optimizer into the API surface.

Recommended direction:
- Add `POST /api/scrape` (single URL)
- Add a background job queue to handle long-running scrapes:
  - Celery + Redis, RQ, Dramatiq, or a managed queue
- Persist jobs + progress in a `ScrapeJob` table (recommended) and render queue status on `/scraper`.

### 2) Jinja mapping / real data loops
Replace static placeholder rows in:
- `templates/app/inventory.html`
- `templates/app/order_history.html`

…with real SQLAlchemy queries and Jinja loops.

### 3) Stripe webhooks & plan enforcement
Implement subscription lifecycle:
- Create Checkout sessions and Customer Portal sessions.
- Add webhook receiver:
  - update `User.active_plan`
  - update `User.sku_limit`
  - store `User.stripe_customer_id`
- Validate success/cancel return pages.

### 4) Production hardening
- CSRF protection for auth + forms (Flask-WTF)
- Rate limiting for `/login` + `/forgot-password`
- Proper password reset tokens (already implemented) + optionally store token hashes / usage tracking
- Centralized config management and secret rotation strategy

---

## Setup Instructions

### 1) Create virtualenv and install
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Configure environment
```bash
cp .env.example .env
```
Fill in `SECRET_KEY`, `VAULT_ENCRYPTION_KEY`, and optionally SMTP settings.

### 3) Run migrations
```bash
export FLASK_APP=app.py
flask db upgrade
```

### 4) Run the app
```bash
python app.py
```
Then visit: http://127.0.0.1:5000

---

## Repo Map (high level)

- `app.py` — Flask app, auth, routes, mail helper, reset tokens
- `models.py` — database models + SupplierVault encryption helpers
- `migrations/` — Alembic migrations
- `templates/layouts/` — base templates (marketing/app)
- `templates/app/` — logged-in UI pages
- `templates/auth/` — password recovery pages
- `templates/emails/` — transactional emails
- `templates/public/` — reusable legal page
