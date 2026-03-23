# Multi-Tenant Auth Visual Guide

## 1) High-Level System View

```mermaid
flowchart LR
    C[Client App] -->|tenant_id + email + password| A[Auth API - Django/DRF]
    A --> D[(PostgreSQL)]
    A --> R[(Redis Cache)]
    A --> J[JWT Access/Refresh Tokens]
    C -->|Bearer Access Token| P[Protected APIs]
    P -->|Validate JWT + tenant + role| A
    P --> D
```

## 2) Data Model (Schema)

```mermaid
erDiagram
    TENANT ||--o{ USER : has

    TENANT {
      uuid id PK
      string slug "unique"
      string name
      bool is_active
      datetime created_at
      datetime updated_at
    }

    USER {
      uuid id PK
      uuid tenant_id FK
      string email
      string role "admin|user"
      bool is_active
      bool is_staff
      datetime created_at
      datetime updated_at
    }
```

> DB rule: unique `(tenant_id, email)`  
> Meaning: same email can exist in different tenants, not duplicated in one tenant.

## 3) Signup Flow

```mermaid
sequenceDiagram
    participant Client
    participant AuthAPI as Auth API
    participant DB as PostgreSQL

    Client->>AuthAPI: POST /auth/signup (tenant_id, email, password, role)
    AuthAPI->>DB: Check tenant exists + active
    AuthAPI->>DB: Check (tenant_id,email) not used
    AuthAPI->>DB: Create user (hashed password)
    AuthAPI-->>Client: 201 + access token + refresh token + user info
```

## 4) Login Flow

```mermaid
sequenceDiagram
    participant Client
    participant AuthAPI as Auth API
    participant Backend as TenantEmailBackend
    participant DB as PostgreSQL

    Client->>AuthAPI: POST /auth/login (tenant_id,email,password)
    AuthAPI->>Backend: authenticate(...)
    Backend->>DB: Find user by tenant_id + email
    Backend->>Backend: verify password hash
    Backend-->>AuthAPI: user (if valid)
    AuthAPI-->>Client: access token + refresh token
```

## 5) Protected API Flow (`/me`, `admin-only`)

```mermaid
sequenceDiagram
    participant Client
    participant API as Protected API
    participant JWT as JWT Auth
    participant Perm as Permissions

    Client->>API: GET /api/v1/auth/me (Bearer token)
    API->>JWT: Validate signature + expiry
    JWT-->>API: request.user + token claims
    API->>Perm: IsTenantMember (token tenant == user tenant)
    Perm-->>API: allow/deny
    API-->>Client: response
```

For `admin-only`, one more check runs:
- `IsAdminRole` -> `user.role == "admin"`

## 6) Isolation Guardrails

```mermaid
flowchart TD
    T[JWT has tenant_id] --> A[Permission check tenant match]
    A --> B[Role check admin/user]
    B --> C[Query by tenant_id]
    C --> D[(DB constraints)]
    D --> E[No cross-tenant data leak]
```

