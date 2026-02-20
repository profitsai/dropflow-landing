# DropFlow Landing Page & Dashboard

A Flask-powered marketing site and SaaS dashboard UI for DropFlow — the dropshipping automation engine for high-volume eBay sellers.

## Quick Start

```bash
pip install -r requirements.txt
python app.py
```

Then visit **http://localhost:5000/**

## Project Structure

```
├── app.py                  # Flask application & routes
├── requirements.txt        # Python dependencies (Flask)
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

## Tech Stack

- **Backend:** Flask (Jinja2 templating)
- **CSS:** Tailwind CSS v3 (CDN)
- **Interactivity:** Alpine.js (CDN) — all UI state is client-side
- **Charts:** ApexCharts (dashboard)
- **Date Picker:** Flatpickr (dashboard)

## Notes for Developers

- All templates use Jinja2 `{% extends %}` / `{% block %}` inheritance
- Marketing pages extend `base.html` — includes nav, footer, scroll animations
- Dashboard pages extend `dashboard_base.html` — includes sidebar, Alpine.js toast store
- Internal links use Flask `url_for()` or relative paths (`/dashboard`, `/products`, etc.)
- No database — all data is mock/static Alpine.js arrays for demo purposes
- `[x-cloak]` CSS rule is included for clean Alpine.js transitions
