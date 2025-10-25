# 🚗 Django Vehicle Rental & Repair Management API
Backend for managing **vehicle rentals, repair orders, and payments** — built with **Django 5 + Django REST Framework + PostgreSQL**.  
Project showcases modular app design, layered serializers/validators, and production-ready environment separation.
---

## 🧩 Project Structure
src/
└── apps/
├── core/
├── rentals/
├── repairs/
├── payments/
└── customers/

## ⚙️ Tech Stack

| Layer       | Tools                              |
|--------------|------------------------------------|
| Backend      | Django 5.2.7, DRF 3.15             |
| Database     | PostgreSQL 15                      |
| API Docs     | drf-spectacular (Swagger UI)       |
| Env Config   | django-environ                     |

---

## 🚀 Setup Instructions

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/AhmHknYildirim/exampleproject.git
cd vehicle-rental-api
```

Create Virtual Environment
```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
Example .env file:

DJANGO_SECRET_KEY=/*/
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
DJANGO_CSRF_TRUSTED_ORIGINS=http://127.0.0.1:8000,http://localhost:8000

POSTGRES_DB=localdb
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

```bash
python manage.py makemigrations
python manage.py migrate

python manage.py loaddata src/apps/core/fixtures/statuses.json
python manage.py runserver
```
Swagger UI → http://127.0.0.1:8000/api/docs/

You must run loaddata statuses.json before using repair or payment endpoints.

EXAMPLE USAGE
POST /api/v1/vehicles/
{
  "text": "Tesla",
  "model": "Model 3",
  "year": 2024,
  "vin": "5YJ3E1EA7JF000001"
}

POST /api/v1/customers/
{
  "first_name": "Ada",
  "last_name": "Lovelace",
  "email": "ada@example.com",
  "identity_number": "12345678901"
}

---
MIT License © 2025 Ahmet Hakan Yıldırım