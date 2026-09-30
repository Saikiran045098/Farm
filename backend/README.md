# FarmBuddy — Backend (Python Django)

A Django REST Framework application providing the backend APIs and database models for FarmBuddy.

## Setup & Running

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run migrations
python manage.py migrate

# 3. Seed data (categories, products, demo users, orders)
python manage.py seed_data

# 4. Start the server on port 8000
python manage.py runserver 8000
```

## Running Tests

```bash
python test_api.py
```
