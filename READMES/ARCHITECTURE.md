# MSuite Architecture Documentation

## 🏗️ System Architecture Overview

MSuite is a production-ready hierarchical multi-tenant SaaS platform providing complete e-commerce backend infrastructure. The system implements a shared database architecture with row-level tenant isolation.

---

## 📊 Hierarchical Multi-Tenancy Model

```
┌─────────────────────────────────────────────────────────────┐
│                        Super Admin                          │
│         (System-wide access & management)                   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ Manages
                       │
         ┌─────────────┴─────────────┬────────────────┐
         │                           │                │
┌────────▼────────┐      ┌──────────▼─────────┐     │
│    Agency 1     │      │     Agency 2       │    ...
│  (Agency Admin) │      │   (Agency Admin)   │
└────────┬────────┘      └──────────┬─────────┘
         │                           │
         │ Creates & Manages         │
         │                           │
    ┌────┴────┬─────────┐      ┌────┴────┬────────┐
    │         │         │      │         │        │
┌───▼───┐ ┌──▼───┐ ┌──▼───┐ ┌─▼────┐ ┌──▼────┐  ...
│Store 1│ │Store2│ │Store3│ │Store4│ │Store5│
│(User) │ │(User)│ │(User)│ │(User)│ │(User)│
└───────┘ └──────┘ └──────┘ └──────┘ └──────┘
```

### Roles & Responsibilities

| Role | Access Level | Capabilities |
|------|-------------|--------------|
| **Super Admin** | System-wide | • Manage agencies and subscription plans<br>• System configuration<br>• View all data across tenants<br>• No direct e-commerce operations |
| **Agency Admin** | Agency-scoped | • Create and manage e-commerce tenants<br>• Manage agency users<br>• View tenant statistics<br>• No direct product/order management |
| **E-commerce User** | Tenant-scoped | • Full CRUD on products, orders, customers<br>• Manage coupons, webhooks, reviews<br>• Access only their tenant's data<br>• Cannot access other tenants |

---

## 🗄️ Database Architecture

### Shared Database Multi-Tenancy

MSuite uses a **shared database** approach where:
- All tenants share the same PostgreSQL database
- Row-level isolation via `agency_id` and `ecommerce_id` foreign keys
- Automatic tenant filtering through dependency injection
- No cross-tenant data leakage

### Schema Design

```
┌──────────────────┐
│ SubscriptionPlan │ ← Super Admin manages
└────────┬─────────┘
         │ 1:N
         │
┌────────▼─────────┐
│     Agency       │ ← Agency Admin context
│   (agency_id)    │
└────────┬─────────┘
         │ 1:N
         │
┌────────▼─────────┐
│    Ecommerce     │ ← E-commerce tenant boundary
│  (ecommerce_id)  │
└────────┬─────────┘
         │
         ├─── Products (with Inventory, Reviews)
         ├─── Orders (with OrderItems)
         ├─── Customers (with Carts, Reviews)
         ├─── Coupons
         ├─── Webhooks
         └─── Cart (with CartItems)

┌──────────────────┐
│   Global Tables  │
├──────────────────┤
│ • Users          │ ← Can belong to Agency or Ecommerce
│ • TokenBlacklist │ ← Session management
│ • AuditLog       │ ← Cross-tenant audit trail
└──────────────────┘
```

### Key Tables (19 Total)

| Table | Purpose | Tenant Scope |
|-------|---------|--------------|
| `users` | Authentication & authorization | Global |
| `subscription_plans` | Pricing tiers | Global (Super Admin) |
| `agencies` | Agency management | Agency-level |
| `ecommerce` | E-commerce tenants | Agency-owned |
| `products` | Product catalog | Tenant-scoped |
| `inventory` | Stock management | Tenant-scoped |
| `orders` | Order processing | Tenant-scoped |
| `order_items` | Order line items | Tenant-scoped |
| `customers` | Customer profiles | Tenant-scoped |
| `carts` | Shopping carts | Tenant-scoped |
| `cart_items` | Cart line items | Tenant-scoped |
| `coupons` | Discount codes | Tenant-scoped |
| `webhooks` | Event notifications | Tenant-scoped |
| `webhook_deliveries` | Delivery tracking | Tenant-scoped |
| `product_reviews` | Customer reviews | Tenant-scoped |
| `audit_logs` | Change tracking | Cross-tenant |
| `token_blacklist` | Revoked tokens | Global |

---

## 🔄 Application Architecture

### Layered Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    HTTP/REST API Layer                  │
│                   (FastAPI Routers)                     │
├─────────────────────────────────────────────────────────┤
│        12 Routers: auth, admin, agency, user,          │
│    product, order, customer, cart, coupon, webhook,    │
│              review, audit_log                          │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              Business Logic Layer                       │
│                 (Service Classes)                       │
├─────────────────────────────────────────────────────────┤
│    AuthService, UserService, ProductService,           │
│    OrderService, CouponService, WebhookService, etc.   │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│               Data Access Layer                         │
│            (SQLAlchemy ORM Models)                      │
├─────────────────────────────────────────────────────────┤
│          14 Models with typed relationships            │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                  Database Layer                         │
│               (PostgreSQL@14)                           │
└─────────────────────────────────────────────────────────┘
```

### Component Interaction Flow

```
Client Request
      │
      ▼
┌──────────────┐
│   FastAPI    │ ← CORS, Request Validation
│  Middleware  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Router     │ ← Route definition, path params
│  (Endpoint)  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Dependencies │ ← Authentication, DB session
│   (DI Layer) │   Tenant context injection
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Service    │ ← Business logic, validations
│    Layer     │   Cross-cutting concerns
└──────┬───────┘
       │
       ▼
┌──────────────┐
│     ORM      │ ← Query building, relationships
│    Model     │   Tenant filtering
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  PostgreSQL  │ ← Data persistence
│   Database   │
└──────────────┘
```

---

## 🔐 Security Architecture

### Authentication Flow

```
┌──────────┐                                      ┌──────────┐
│  Client  │                                      │  Server  │
└─────┬────┘                                      └─────┬────┘
      │                                                 │
      │  POST /api/v1/auth/login                      │
      │  { email, password }                          │
      │────────────────────────────────────────────►  │
      │                                                 │
      │                                           ┌─────▼─────┐
      │                                           │  Validate │
      │                                           │Credentials│
      │                                           └─────┬─────┘
      │                                                 │
      │  ◄─────────────────────────────────────────────┤
      │  { access_token, refresh_token, user }         │
      │                                                 │
      │  GET /api/v1/products                          │
      │  Header: Authorization: Bearer <token>         │
      │────────────────────────────────────────────►  │
      │                                                 │
      │                                           ┌─────▼─────┐
      │                                           │Verify JWT │
      │                                           │Check      │
      │                                           │Blacklist  │
      │                                           │Check      │
      │                                           │Session    │
      │                                           │Timeout    │
      │                                           └─────┬─────┘
      │                                                 │
      │                                           ┌─────▼─────┐
      │                                           │Get User   │
      │                                           │Context    │
      │                                           │Update     │
      │                                           │Activity   │
      │                                           └─────┬─────┘
      │                                                 │
      │  ◄─────────────────────────────────────────────┤
      │  { products: [...] }                           │
      │                                                 │
```

### Token Management

1. **Access Token**
   - Lifetime: 60 minutes
   - Contains: user_id, email, role, agency_id, ecommerce_id
   - Used for API authentication

2. **Refresh Token**
   - Lifetime: 7 days
   - Used to obtain new access tokens
   - Stored securely by client

3. **Token Blacklist**
   - Tracks revoked tokens (logout, timeout)
   - Checked on every authenticated request
   - Auto-cleanup on token expiry

### Session Management

- **30-minute inactivity timeout**
- Automatic activity tracking on every request
- Session extension available via API
- Clear error messages on expiry

---

## 🔄 Data Flow Patterns

### Order Creation Flow

```
Client → POST /api/v1/orders
   │
   ▼
Authenticate User
   │
   ▼
Get Tenant Context (ecommerce_id)
   │
   ▼
Validate Customer exists in tenant
   │
   ▼
Validate Products exist and in stock
   │
   ▼
BEGIN TRANSACTION
   │
   ├─► Create Order record
   │
   ├─► Create OrderItem records
   │
   ├─► Reserve Inventory
   │       (quantity → reserved_quantity)
   │
   ├─► Apply Coupon (if provided)
   │       Validate & increment usage
   │
   ├─► Calculate Totals
   │       subtotal, tax, shipping, discount
   │
   ├─► Trigger Webhook
   │       Event: ORDER_CREATED
   │
   └─► Create Audit Log
           Action: ORDER_CREATE
COMMIT TRANSACTION
   │
   ▼
Return Order with Items
```

### Webhook Delivery Flow

```
Event Triggered (e.g., ORDER_CREATED)
   │
   ▼
Get Active Webhooks for Event Type
   │
   ▼
For Each Webhook:
   │
   ├─► Prepare Payload
   │      { event, data, timestamp }
   │
   ├─► Generate HMAC Signature
   │      Using webhook secret
   │
   ├─► Send HTTP POST
   │      Headers: X-Signature, X-Event
   │
   ├─► Record Delivery Attempt
   │      { status, response, attempt }
   │
   └─► If Failed:
          Schedule Retry
          Exponential backoff: 2^attempt minutes
```

---

## 🎯 Dependency Injection Pattern

### Tenant Context Injection

All tenant-scoped operations automatically filter by tenant:

```python
# In dependencies.py
async def get_current_user(token: str, db: Session) -> User:
    # Validates token, checks blacklist, updates activity
    user = authenticate(token)
    return user

# Usage in router
@router.get("/products")
def list_products(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Automatically filtered by current_user.ecommerce_id
    products = db.query(Product).filter(
        Product.ecommerce_id == current_user.ecommerce_id
    ).all()
    return products
```

### Benefits

- ✅ No manual tenant filtering in business logic
- ✅ Impossible to access other tenant's data
- ✅ Centralized security enforcement
- ✅ Type-safe with Python type hints

---

## 📈 Scalability Considerations

### Current Architecture

- **Vertical Scaling:** Single PostgreSQL instance
- **Connection Pooling:** SQLAlchemy manages connections
- **Stateless API:** Horizontal scaling ready
- **JWT Authentication:** No session storage needed

### Future Enhancements

1. **Read Replicas**
   - Separate read/write connections
   - Load balance read queries

2. **Caching Layer**
   - Redis for frequently accessed data
   - Product catalog, user sessions

3. **Message Queue**
   - Async webhook delivery
   - Background job processing

4. **Microservices (if needed)**
   - Separate services for webhooks, notifications
   - Event-driven architecture

---

## 🔍 Monitoring & Observability

### Audit Logging

Every system change is tracked:
- User actions (login, logout, CRUD operations)
- Resource modifications (old vs new values)
- Request metadata (IP address, user agent)
- Tenant context (agency_id, ecommerce_id)

### Webhook Delivery Tracking

All webhook deliveries are logged:
- Success/failure status
- HTTP response codes
- Retry attempts
- Delivery timestamps

---

## 🏗️ Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Web Framework** | FastAPI | High-performance async API framework |
| **ORM** | SQLAlchemy 2.0 | Database abstraction, typed relationships |
| **Database** | PostgreSQL@14 | Relational data storage |
| **Migrations** | Alembic | Schema version control |
| **Authentication** | JWT (python-jose) | Stateless token-based auth |
| **Password Hashing** | bcrypt | Secure password storage |
| **Validation** | Pydantic v2 | Request/response validation |
| **HTTP Client** | httpx | Async webhook delivery |
| **Dependency Management** | Poetry | Python package management |

---

## 🎨 Design Patterns Used

1. **Repository Pattern** - Service layer abstracts data access
2. **Dependency Injection** - FastAPI's DI system for loose coupling
3. **Factory Pattern** - Token creation, service initialization
4. **Strategy Pattern** - Coupon discount types
5. **Observer Pattern** - Webhook event notifications
6. **Chain of Responsibility** - Request middleware, validation pipeline

---

## 📚 Related Documentation

- [Features Details](FEATURES.md) - Comprehensive feature descriptions
- [API Documentation](ROUTES_SUMMARY.md) - All 82 endpoints
- [Setup Guide](SETUP_GUIDE.md) - Installation and configuration
- [Project Structure](PROJECT_STRUCTURE.md) - File organization
- [Implementation Guide](IMPLEMENTATION_GUIDE.md) - Technical implementation details
