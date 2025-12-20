# MSuite - Project Structure

## 📁 Directory Organization

```
msuite-server/
├── 📄 pyproject.toml              # Poetry dependencies & project config
├── 📄 poetry.toml                 # Poetry settings (in-project venv)
├── 📄 poetry.lock                 # Locked dependencies
│
├── 📁 alembic/                    # Database migrations
│   ├── versions/                  # Migration files
│   │   ├── 3743490f158a_initial.py
│   │   ├── c182cdb29432_add_phase_5_features.py
│   │   └── 03aac0dc2e7f_add_logout_and_session_management.py
│   ├── env.py                     # Migration environment config
│   ├── script.py.mako            # Migration template
│   └── alembic.ini               # Alembic configuration
│
├── 📁 app/                        # Main application package
│   ├── __init__.py
│   ├── 📄 main.py                # FastAPI app initialization & router registration
│   │
│   ├── 📁 core/                  # Core infrastructure
│   │   ├── __init__.py
│   │   ├── config.py             # Environment settings (BaseSettings)
│   │   ├── database.py           # Database connection & session
│   │   ├── security.py           # JWT, password hashing, token utils
│   │   └── dependencies.py       # Dependency injection (auth, DB)
│   │
│   ├── 📁 enums/                 # Enumeration types
│   │   ├── __init__.py
│   │   └── user_role.py          # UserRole enum (SUPER_ADMIN, AGENCY_ADMIN, ECOMMERCE)
│   │
│   ├── 📁 models/                # SQLAlchemy ORM models (14 models)
│   │   ├── __init__.py           # Model exports
│   │   ├── user.py               # User authentication & roles
│   │   ├── agency.py             # Agency management
│   │   ├── subscription.py       # Subscription plans
│   │   ├── ecommerce.py          # E-commerce tenants
│   │   ├── product.py            # Product catalog
│   │   ├── order.py              # Orders & OrderItems
│   │   ├── customer.py           # Customer profiles
│   │   ├── inventory.py          # Stock management
│   │   ├── cart.py               # Shopping carts
│   │   ├── coupon.py             # Discount coupons
│   │   ├── webhook.py            # Webhooks & deliveries
│   │   ├── review.py             # Product reviews
│   │   ├── audit_log.py          # System audit trail
│   │   └── token_blacklist.py    # Revoked JWT tokens
│   │
│   ├── 📁 schemas/               # Pydantic validation schemas
│   │   ├── __init__.py
│   │   ├── auth.py               # Login, Register, Token responses
│   │   ├── user.py               # User CRUD schemas
│   │   ├── product.py            # Product CRUD schemas
│   │   ├── subscription.py       # Subscription plan schemas
│   │   ├── coupon.py             # Coupon schemas
│   │   ├── review.py             # Review schemas
│   │   └── audit_log.py          # Audit log schemas
│   │
│   ├── 📁 services/              # Business logic layer (12 services)
│   │   ├── __init__.py
│   │   ├── auth_service.py       # Authentication, logout, session mgmt
│   │   ├── user_service.py       # User CRUD operations
│   │   ├── product_service.py    # Product management
│   │   ├── subscription_service.py # Subscription plans
│   │   ├── coupon_service.py     # Coupon validation & usage
│   │   ├── webhook_service.py    # Webhook delivery & signatures
│   │   ├── review_service.py     # Review moderation & stats
│   │   └── audit_log_service.py  # Audit logging
│   │
│   ├── 📁 routers/               # API route handlers (12 routers)
│   │   ├── __init__.py
│   │   ├── auth.py               # Authentication endpoints (7)
│   │   ├── super_admin.py        # Super admin operations (10)
│   │   ├── agency_admin.py       # Agency admin operations (6)
│   │   ├── user.py               # User management (6)
│   │   ├── product.py            # Product endpoints (6)
│   │   ├── order.py              # Order endpoints (5)
│   │   ├── customer.py           # Customer endpoints (6)
│   │   ├── cart.py               # Cart endpoints (5)
│   │   ├── coupon.py             # Coupon endpoints (6)
│   │   ├── webhook.py            # Webhook endpoints (8)
│   │   ├── review.py             # Review endpoints (9)
│   │   └── audit_log.py          # Audit log endpoints (4)
│   │
│   ├── 📁 middleware/            # Custom middleware
│   │   ├── __init__.py
│   │   └── activity_tracking.py  # Session activity tracking
│   │
│   └── 📁 utils/                 # Utility functions
│       ├── __init__.py
│       └── time.py               # Time/date utilities
│
├── 📁 .venv/                      # Virtual environment (gitignored)
│
└── 📁 docs/                       # Documentation (you are here!)
    ├── 📄 README.md               # Project hub & quick links
    ├── 📄 ARCHITECTURE.md         # System architecture & design
    ├── 📄 FEATURES.md             # Feature descriptions & flows
    ├── 📄 PROJECT_STRUCTURE.md    # This file
    ├── 📄 SETUP_GUIDE.md          # Installation & setup
    ├── 📄 ROUTES_SUMMARY.md       # API endpoints (82 total)
    ├── 📄 IMPLEMENTATION_GUIDE.md # Implementation details
    └── 📄 SESSION_MANAGEMENT_IMPLEMENTATION.md # Session features
```

---

## 🎯 Module Responsibilities

### Core Package (`app/core/`)

**Purpose:** Foundation infrastructure for the application

| File | Responsibility |
|------|----------------|
| `config.py` | Environment variables, settings management using Pydantic BaseSettings |
| `database.py` | SQLAlchemy engine, session factory, connection pooling |
| `security.py` | JWT token creation/verification, password hashing (bcrypt), security utilities |
| `dependencies.py` | Dependency injection functions: authentication, database sessions, tenant context |

**Key Functions:**
- `get_db()` - Database session dependency
- `get_current_user()` - Extract & validate user from JWT, check blacklist, update activity
- `create_access_token()` - Generate JWT access tokens
- `verify_password()` - Validate user passwords

---

### Models Package (`app/models/`)

**Purpose:** SQLAlchemy ORM models representing database tables

| Model | Table | Purpose |
|-------|-------|---------|
| `User` | users | Authentication, roles, tenant associations |
| `Agency` | agencies | Agency management (for Agency Admins) |
| `SubscriptionPlan` | subscription_plans | Pricing tiers |
| `Ecommerce` | ecommerce | E-commerce tenant definitions |
| `Product` | products | Product catalog |
| `Inventory` | inventory | Stock levels (available, reserved) |
| `Order` | orders | Order headers |
| `OrderItem` | order_items | Order line items |
| `Customer` | customers | Customer profiles & addresses |
| `Cart` | carts | Shopping cart headers |
| `CartItem` | cart_items | Cart line items |
| `Coupon` | coupons | Discount codes |
| `Webhook` | webhooks | Webhook configurations |
| `WebhookDelivery` | webhook_deliveries | Delivery attempts & results |
| `ProductReview` | product_reviews | Customer reviews & ratings |
| `AuditLog` | audit_logs | System audit trail |
| `TokenBlacklist` | token_blacklist | Revoked JWT tokens |

**Relationships:**
- All models use SQLAlchemy 2.0 typed relationships (`Mapped[]`)
- Cascade deletes configured for data integrity
- Indexes on foreign keys for query performance

---

### Schemas Package (`app/schemas/`)

**Purpose:** Pydantic v2 models for request/response validation

| Schema | Purpose |
|--------|---------|
| `auth.py` | LoginRequest, RegisterRequest, TokenResponse, UserResponse |
| `user.py` | UserCreate, UserUpdate, UserResponse |
| `product.py` | ProductCreate, ProductUpdate, ProductResponse, InventoryUpdate |
| `subscription.py` | SubscriptionPlanCreate, SubscriptionPlanResponse |
| `coupon.py` | CouponCreate, CouponValidation, CouponResponse |
| `review.py` | ReviewCreate, ReviewModeration, ReviewStats |
| `audit_log.py` | AuditLogResponse, AuditLogFilter |

**Features:**
- Automatic validation of request payloads
- Type coercion and error messages
- Response serialization
- `ConfigDict` for ORM compatibility

---

### Services Package (`app/services/`)

**Purpose:** Business logic layer separating concerns from routes

| Service | Responsibilities |
|---------|------------------|
| `AuthService` | Login, register, token generation, logout, session management |
| `UserService` | User CRUD, role validation |
| `ProductService` | Product management, inventory updates |
| `SubscriptionService` | Subscription plan CRUD |
| `CouponService` | Coupon validation, discount calculation, usage tracking |
| `WebhookService` | Event delivery, HMAC signatures, retry logic |
| `ReviewService` | Review CRUD, moderation, statistics calculation |
| `AuditLogService` | Audit log creation, filtering, resource history |

**Pattern:**
- Static methods for stateless operations
- Database session passed as parameter
- Returns domain models or DTOs
- Raises HTTPException on business rule violations

---

### Routers Package (`app/routers/`)

**Purpose:** API endpoint definitions (FastAPI routers)

**Total Endpoints:** 82 (80 API + 2 health checks)

| Router | Endpoints | Base Path |
|--------|-----------|-----------|
| `auth.py` | 7 | `/api/v1/auth` |
| `super_admin.py` | 10 | `/api/v1/admin` |
| `agency_admin.py` | 6 | `/api/v1/agencies` |
| `user.py` | 6 | `/api/v1/users` |
| `product.py` | 6 | `/api/v1/products` |
| `order.py` | 5 | `/api/v1/orders` |
| `customer.py` | 6 | `/api/v1/customers` |
| `cart.py` | 5 | `/api/v1/cart` |
| `coupon.py` | 6 | `/api/v1/coupons` |
| `webhook.py` | 8 | `/api/v1/webhooks` |
| `review.py` | 9 | `/api/v1/reviews` |
| `audit_log.py` | 4 | `/api/v1/audit-logs` |

**Conventions:**
- Async functions for I/O operations
- Dependency injection for auth & DB
- Status codes via `status.HTTP_*` constants
- Response models for type safety

---

## 🔄 Request Flow Through Structure

### Example: GET /api/v1/products

```
1. Client Request
   GET http://localhost:8000/api/v1/products
   Header: Authorization: Bearer <token>

2. app/main.py
   FastAPI receives request
   → CORS middleware
   → Route matching

3. app/routers/product.py
   @router.get("")
   → Dependencies executed:
     - get_db() → Database session
     - get_current_user() → User authentication

4. app/core/dependencies.py::get_current_user()
   → Extract token from header
   → Check token_blacklist table
   → Decode JWT
   → Query users table
   → Check session timeout
   → Update last_activity
   → Return User object

5. app/routers/product.py
   → Route handler receives: (current_user, db)
   → Call ProductService.get_products()

6. app/services/product_service.py
   → Business logic: filter by current_user.ecommerce_id
   → Query products table
   → Return list of Product models

7. app/routers/product.py
   → Convert to ProductResponse schemas
   → Return JSON response

8. Client receives response
   Status: 200 OK
   Body: [{ product1 }, { product2 }, ...]
```

---

## 🗂️ Configuration Files

### pyproject.toml

```toml
[tool.poetry]
name = "msuite-server"
version = "1.0.0"
description = "Multi-tenant E-Commerce Backend-as-a-Service"

[tool.poetry.dependencies]
python = "^3.12"
fastapi = "^0.104.0"
uvicorn = "^0.24.0"
sqlalchemy = "^2.0.0"
alembic = "^1.12.0"
psycopg2-binary = "^2.9.9"
python-jose = {extras = ["cryptography"], version = "^3.3.0"}
passlib = {extras = ["bcrypt"], version = "^1.7.4"}
bcrypt = "4.3.0"
python-multipart = "^0.0.6"
pydantic = {extras = ["email"], version = "^2.0.0"}
pydantic-settings = "^2.0.0"
httpx = "^0.28.1"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"
```

### poetry.toml

```toml
[virtualenvs]
in-project = true
```

Forces virtual environment creation inside project (`.venv/`)

### alembic.ini

```ini
[alembic]
script_location = alembic
sqlalchemy.url = postgresql://msuite_user:msuite_password@localhost/MSuite
```

Database migration configuration

---

## 📊 Code Statistics

| Metric | Count |
|--------|-------|
| **Total Lines of Code** | ~8,500+ |
| **Models** | 14 |
| **Services** | 12 |
| **Routers** | 12 |
| **Schemas** | 15+ |
| **API Endpoints** | 82 |
| **Database Tables** | 19 |
| **Migrations** | 3 |
| **Python Version** | 3.12+ |

---

## 🎨 Naming Conventions

### Files & Modules
- **Snake case:** `auth_service.py`, `user_role.py`
- **Descriptive names:** Service, Router, Model suffix where applicable

### Classes
- **PascalCase:** `User`, `ProductService`, `AuthRouter`
- **Suffixes:** `Service`, `Response`, `Create`, `Update`

### Functions & Methods
- **Snake case:** `get_current_user()`, `create_access_token()`
- **Action verbs:** `get_`, `create_`, `update_`, `delete_`

### Variables
- **Snake case:** `user_id`, `ecommerce_id`, `access_token`
- **Descriptive:** Avoid abbreviations unless common (id, db, pk)

### Database
- **Table names:** Plural, snake_case (`users`, `order_items`)
- **Column names:** Snake_case (`created_at`, `ecommerce_id`)
- **Foreign keys:** `{table}_id` pattern

---

## 🔍 Finding Your Way Around

### "I need to add a new endpoint"
1. Create/modify schema in `app/schemas/`
2. Add business logic in `app/services/`
3. Create route in `app/routers/`
4. Register router in `app/main.py`

### "I need to add a new database table"
1. Create model in `app/models/`
2. Export in `app/models/__init__.py`
3. Generate migration: `alembic revision --autogenerate`
4. Apply migration: `alembic upgrade head`

### "I need to modify authentication"
- Logic: `app/services/auth_service.py`
- Dependencies: `app/core/dependencies.py`
- Security utils: `app/core/security.py`
- Routes: `app/routers/auth.py`

### "I need to add tenant filtering"
- Add `ecommerce_id` foreign key to model
- Use `current_user.ecommerce_id` in service
- Dependency injection handles the rest

---

## 📚 Related Documentation

- [Architecture Overview](ARCHITECTURE.md) - System design & patterns
- [Features Guide](FEATURES.md) - What the system does
- [API Documentation](ROUTES_SUMMARY.md) - All endpoints
- [Setup Instructions](SETUP_GUIDE.md) - Getting started
