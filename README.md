# DropFlow Landing Page

## Setup
```bash
pip install flask
python app.py
```

Then visit **http://localhost:5000/**

## Structure
```
app.py              # Flask routes
templates/          # Jinja2 templates (base.html, dashboard_base.html, + all pages)
static/             # Static assets (images)
requirements.txt    # Dependencies
```

## Pages
| Route | Template | Description |
|-------|----------|-------------|
| `/` | index.html | Landing page |
| `/pricing` | pricing.html | Pricing tiers |
| `/login` | login.html | Login page |
| `/signup` | signup.html | Signup page |
| `/dashboard` | dashboard.html | Dashboard |
| `/products` | products.html | Product catalog |
| `/orders` | orders.html | Order management |
| `/import` | import.html | Import console |
| `/scraper` | scraper.html | Store scraper |
| `/settings` | settings.html | Settings |

