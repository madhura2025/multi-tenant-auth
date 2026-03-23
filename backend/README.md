# Multi-Tenant Auth (Django)

This project is a starter backend for multi-tenant authentication and authorization.

Architecture diagrams: see `ARCHITECTURE.md`.

## Features

- Tenant model (`tenants.Tenant`)
- Custom user model (`accounts.User`) with:
  - `tenant` reference
  - `email`
  - `role` (`admin`, `user`)
- Same email allowed across different tenants
- Login requires `tenant_id + email + password`
- JWT auth (access + refresh, refresh rotation enabled)
- Role-protected endpoint example (`admin-only`)

## Quickstart

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy env file:

```bash
cp .env.example .env
```

4. Run migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

5. Start server:

```bash
python manage.py runserver
```

## API Endpoints

- `POST /api/v1/auth/signup/`
- `POST /api/v1/auth/login/`
- `POST /api/v1/auth/refresh/`
- `POST /api/v1/auth/logout/`
- `GET /api/v1/auth/me/`
- `GET /api/v1/auth/admin-only/`
- `POST /api/v1/simple-auth/login/` (email + password only)

## Sample Login Payload

```json
{
  "tenant_id": "uuid-here",
  "email": "user@example.com",
  "password": "your-password"
}
```
