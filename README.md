# FarmBuddy — Fullstack Village Marketplace

FarmBuddy has been separated into independent **Frontend** and **Backend** directories:
- **`frontend/`**: Next.js 16 (App Router), React 19, TypeScript, Framer Motion, and Tailwind CSS.
- **`backend/`**: Python 3.11, Django 5, Django REST Framework (DRF), and django-cors-headers.

---

## Project Structure

```
Farm/
├── frontend/                     # Next.js Frontend Application
│   ├── src/
│   │   ├── app/                 # Next.js App Router pages & routes
│   │   ├── components/          # React components (Market, Admin, Cart, etc.)
│   │   ├── data/                # Catalog and local metadata
│   │   ├── i18n/                # English / Telugu bilingual translations
│   │   └── lib/                 # Client & Server API connectors, auth helpers
│   ├── package.json
│   ├── next.config.ts
│   ├── tsconfig.json
│   └── .env.local
│
├── backend/                      # Python Django REST API Backend
│   ├── api/                     # Core API application
│   │   ├── models.py            # Products, Categories, Orders, Users, Cart, etc.
│   │   ├── views.py             # DRF views for all API endpoints
│   │   ├── urls.py              # API URL routing
│   │   ├── auth_utils.py        # Token auth, cookies, password hashing
│   │   ├── seeds.py             # Initial database seed data
│   │   └── admin.py             # Django Admin configuration
│   ├── farmbuddy/               # Django project settings & root URLs
│   ├── manage.py
│   ├── requirements.txt
│   └── test_api.py              # Automated test suite
│
├── start-dev.bat                 # One-click launcher for Windows
├── package.json                  # Root monorepo scripts
└── README.md
```

---

## Quick Start

### 1. Backend (Python Django)

Open a terminal and navigate to `backend/`:

```bash
cd backend

# Install dependencies (if not already installed)
pip install -r requirements.txt

# Run database migrations
python manage.py migrate

# Seed initial categories, products, admin and demo customers
python manage.py seed_data

# Start the Django development server (runs on port 8000)
python manage.py runserver 8000
```

The Django REST API will be available at: **http://127.0.0.1:8000/api/**  
The Django Admin panel will be available at: **http://127.0.0.1:8000/admin/**

### 2. Frontend (Next.js)

In a separate terminal, navigate to `frontend/`:

```bash
cd frontend

# Install Node dependencies
npm install

# Start the Next.js development server
npm run dev
```

The Next.js frontend will be live at: **http://localhost:3000**

---

## Launch Both on Windows (One-Click)

Simply double-click `start-dev.bat` in the root folder, or run:

```cmd
start-dev.bat
```

This opens two terminal windows running the Django backend (`:8000`) and the Next.js frontend (`:3000`) simultaneously.

---

## Automated Backend Test Suite

To verify all backend API endpoints (Health, Categories, Products, Auth, Cart, Admin Stats):

```bash
cd backend
python test_api.py
```

---

## Demo Accounts

| Role | Email | Password |
|---|---|---|
| **Customer** | `customer@farmbuddy.in` | `Village@2026` |
| **Admin** | `admin@farmbuddy.in` | `FarmBuddy@2026` |

*One-click demo buttons are also present in the frontend sign-in modal and `/admin` page.*

---

## Django API Endpoints

- **Health Check**: `GET /api/health`
- **Auth**: `POST /api/auth/register`, `POST /api/auth/login`, `POST /api/auth/logout`, `GET /api/auth/me`
- **Catalog**: `GET/POST /api/products`, `GET/PUT/DELETE /api/products/:id_or_slug`
- **Categories**: `GET/POST /api/categories`, `PUT/DELETE /api/categories/:slug`
- **Basket / Cart**: `GET/POST /api/cart`, `PUT/DELETE /api/cart/:id`
- **Wishlist**: `GET/POST /api/wishlist`, `DELETE /api/wishlist/:productId`
- **Orders**: `GET/POST /api/orders`, `GET /api/orders/:id`, `PUT /api/orders/:id/status`
- **Subscriptions**: `GET/POST /api/subscriptions`, `PUT /api/subscriptions/:id`
- **Users**: `GET /api/users`, `GET/PUT /api/users/:id`
- **Admin Stats**: `GET /api/admin/stats`
- **Contact & Newsletter**: `POST /api/contact`, `POST /api/newsletter`
