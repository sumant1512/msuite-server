# MSuite - Complete Implementation Guide

## 📑 Table of Contents

- [Project Overview](#-project-overview)
- [Architecture Overview](#️-architecture-overview)
- [System Flow Diagrams](#-system-flow-diagrams)
- [Implementation Summary](#-implementation-summary)
- [Component Details](#-component-details)
- [API Endpoints](#-api-endpoints)
- [Database Schema](#️-database-schema)
- [Authentication Flow](#-authentication-flow)
- [Multi-Tenancy Implementation](#-multi-tenancy-implementation)
- [Code Statistics](#-code-statistics)
- [Quality & Security](#-quality--security)
- [Running the Application](#-running-the-application)
- [Testing Guide](#-testing-guide)
- [Future Enhancements](#-future-enhancements)

---

## 🎯 Project Overview

**MSuite** is a production-ready multi-tenant E-Commerce Backend-as-a-Service (BaaS) platform that enables agencies to manage multiple e-commerce stores for their clients.

### Key Capabilities
- 🏢 **Multi-Agency Support** - Super admin manages multiple agencies
- 🛍️ **Multi-Store Management** - Each agency manages multiple e-commerce stores
- 🔐 **Role-Based Access Control** - 3-tier permission system
- 📦 **Complete E-Commerce Suite** - Products, orders, customers, carts, coupons, reviews
- 🔔 **Webhook System** - Real-time event notifications
- 📝 **Audit Logging** - Full compliance tracking
- 🔒 **JWT Authentication** - Secure token-based auth

### Technology Stack
- **Backend:** FastAPI (Python 3.12)
- **Database:** PostgreSQL 14+
- **ORM:** SQLAlchemy 2.0 with async support
- **Migrations:** Alembic
- **Authentication:** JWT (python-jose) + bcrypt
- **Validation:** Pydantic v2

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         MSuite Platform                          │
└─────────────────────────────────────────────────────────────────┘
                                 │
                ┌────────────────┼────────────────┐
                │                │                │
         ┌──────▼──────┐  ┌─────▼─────┐  ┌──────▼──────┐
         │ Super Admin │  │  Agency   │  │  E-commerce │
         │   Layer     │  │  Admin    │  │    Users    │
         └──────┬──────┘  └─────┬─────┘  └──────┬──────┘
                │                │                │
                └────────────────┼────────────────┘
                                 │
         ┌───────────────────────▼───────────────────────┐
         │         Hierarchical Multi-Tenancy            │
         │                                               │
         │  Super Admin → Agency → E-commerce Store     │
         │       │           │            │              │
         │       │           │            └─ Products    │
         │       │           │            └─ Orders      │
         │       │           │            └─ Customers   │
         │       │           │            └─ Carts       │
         │       │           │            └─ Coupons     │
         │       │           │            └─ Reviews     │
         │       │           │            └─ Webhooks    │
         │       │           │                           │
         │       │           └─ Manage E-commerce Stores │
         │       │           └─ View Analytics           │
         │       │                                       │
         │       └─ Manage Agencies                     │
         │       └─ Manage Subscription Plans           │
         │                                               │
         └───────────────────────────────────────────────┘
                                 │
         ┌───────────────────────▼───────────────────────┐
         │            Database Layer                     │
         │  ┌─────────────────────────────────────────┐ │
         │  │  PostgreSQL 14+ (Shared Database)      │ │
         │  │                                         │ │
         │  │  • 18 Tables                           │ │
         │  │  • Row-Level Tenant Isolation          │ │
         │  │  • Foreign Key Constraints             │ │
         │  │  • Indexes on tenant_id columns        │ │
         │  └─────────────────────────────────────────┘ │
         └───────────────────────────────────────────────┘
```

### Layered Architecture

```
┌────────────────────────────────────────────────────────────┐
│                    API Layer (FastAPI)                     │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  Routers (12 modules)                                │ │
│  │  • Authentication  • Cart        • Coupons           │ │
│  │  • Super Admin     • Products    • Webhooks          │ │
│  │  • Agency Admin    • Orders      • Reviews           │ │
│  │  • Users           • Customers   • Audit Logs        │ │
│  └──────────────────────────────────────────────────────┘ │
└─────────────────────┬──────────────────────────────────────┘
                      │
┌─────────────────────▼──────────────────────────────────────┐
│              Service Layer (Business Logic)                │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  Services (12 modules)                               │ │
│  │  • AuthService      • CartService                    │ │
│  │  • UserService      • CouponService                  │ │
│  │  • ProductService   • WebhookService                 │ │
│  │  • OrderService     • ReviewService                  │ │
│  │  • CustomerService  • AuditLogService                │ │
│  │  • SubscriptionService                               │ │
│  └──────────────────────────────────────────────────────┘ │
└─────────────────────┬──────────────────────────────────────┘
                      │
┌─────────────────────▼──────────────────────────────────────┐
│              Data Access Layer (SQLAlchemy)                │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  Models (13 models)                                  │ │
│  │  • User            • Cart/CartItem                   │ │
│  │  • Agency          • Coupon                          │ │
│  │  • Ecommerce       • Webhook/WebhookDelivery         │ │
│  │  • Product         • ProductReview                   │ │
│  │  │  Inventory      • AuditLog                        │ │
│  │  • Order/OrderItem                                   │ │
│  │  • Customer                                          │ │
│  └──────────────────────────────────────────────────────┘ │
└─────────────────────┬──────────────────────────────────────┘
                      │
┌─────────────────────▼──────────────────────────────────────┐
│                   Database (PostgreSQL)                    │
│                      18 Tables                             │
└────────────────────────────────────────────────────────────┘
```

---

## 🔄 System Flow Diagrams

### 1. User Authentication Flow

```
┌─────────┐                                    ┌──────────┐
│ Client  │                                    │  Server  │
└────┬────┘                                    └────┬─────┘
     │                                              │
     │  POST /api/v1/auth/register                 │
     ├─────────────────────────────────────────────>│
     │  { email, password, name, role }            │
     │                                              │
     │                                         ┌────▼────┐
     │                                         │ Validate│
     │                                         │  Data   │
     │                                         └────┬────┘
     │                                              │
     │                                         ┌────▼────┐
     │                                         │  Hash   │
     │                                         │Password │
     │                                         └────┬────┘
     │                                              │
     │                                         ┌────▼────┐
     │                                         │  Save   │
     │                                         │  User   │
     │                                         └────┬────┘
     │  201 Created                                 │
     │<─────────────────────────────────────────────┤
     │  { user_data }                               │
     │                                              │
     │  POST /api/v1/auth/login                    │
     ├─────────────────────────────────────────────>│
     │  { email, password }                        │
     │                                              │
     │                                         ┌────▼────┐
     │                                         │  Find   │
     │                                         │  User   │
     │                                         └────┬────┘
     │                                              │
     │                                         ┌────▼────┐
     │                                         │ Verify  │
     │                                         │Password │
     │                                         └────┬────┘
     │                                              │
     │                                         ┌────▼────┐
     │                                         │Generate │
     │                                         │  Tokens │
     │                                         └────┬────┘
     │  200 OK                                      │
     │<─────────────────────────────────────────────┤
     │  { access_token, refresh_token }            │
     │                                              │
     │  GET /api/v1/products                       │
     │  Authorization: Bearer {access_token}       │
     ├─────────────────────────────────────────────>│
     │                                              │
     │                                         ┌────▼────┐
     │                                         │ Verify  │
     │                                         │  Token  │
     │                                         └────┬────┘
     │                                              │
     │                                         ┌────▼────┐
     │                                         │  Get    │
     │                                         │Products │
     │                                         └────┬────┘
     │  200 OK                                      │
     │<─────────────────────────────────────────────┤
     │  [products...]                               │
     │                                              │
```

### 2. Multi-Tenant Product Creation Flow

```
┌──────────────┐                              ┌─────────────┐
│ E-commerce   │                              │   Server    │
│    User      │                              │             │
└──────┬───────┘                              └──────┬──────┘
       │                                             │
       │  POST /api/v1/products                     │
       │  Authorization: Bearer {token}             │
       │  { name, sku, price, stock }               │
       ├────────────────────────────────────────────>│
       │                                             │
       │                                        ┌────▼────┐
       │                                        │ Extract │
       │                                        │  Token  │
       │                                        └────┬────┘
       │                                             │
       │                                        ┌────▼────┐
       │                                        │  Get    │
       │                                        │  User   │
       │                                        └────┬────┘
       │                                             │
       │                                        ┌────▼─────┐
       │                                        │ Get User │
       │                                        │ecommerce │
       │                                        │   _id    │
       │                                        └────┬─────┘
       │                                             │
       │                                        ┌────▼─────┐
       │                                        │ Create   │
       │                                        │ Product  │
       │                                        │ with     │
       │                                        │ecommerce │
       │                                        │  _id     │
       │                                        └────┬─────┘
       │                                             │
       │                                        ┌────▼─────┐
       │                                        │ Create   │
       │                                        │Inventory │
       │                                        │  Record  │
       │                                        └────┬─────┘
       │                                             │
       │                                        ┌────▼─────┐
       │                                        │ Trigger  │
       │                                        │ Webhook  │
       │                                        │ PRODUCT_ │
       │                                        │ CREATED  │
       │                                        └────┬─────┘
       │                                             │
       │                                        ┌────▼─────┐
       │                                        │  Log     │
       │                                        │  Audit   │
       │                                        │  Trail   │
       │                                        └────┬─────┘
       │  201 Created                                │
       │<────────────────────────────────────────────┤
       │  { id, name, sku, ecommerce_id, ... }      │
       │                                             │
```

### 3. Order Processing Flow

```
┌──────────┐                                      ┌─────────┐
│ Customer │                                      │  Server │
└────┬─────┘                                      └────┬────┘
     │                                                 │
     │  1. Add items to cart                          │
     ├────────────────────────────────────────────────>│
     │  POST /api/v1/cart/{cart_id}/items             │
     │                                                 │
     │  2. Apply coupon (optional)                    │
     ├────────────────────────────────────────────────>│
     │  POST /api/v1/coupons/validate/{code}          │
     │                                            ┌────▼────┐
     │                                            │ Validate│
     │                                            │  Coupon │
     │                                            └────┬────┘
     │  { is_valid, discount_amount }                 │
     │<────────────────────────────────────────────────┤
     │                                                 │
     │  3. Create order                                │
     ├────────────────────────────────────────────────>│
     │  POST /api/v1/orders                            │
     │  { customer_id, items, coupon_code }            │
     │                                            ┌────▼────┐
     │                                            │ Reserve │
     │                                            │Inventory│
     │                                            └────┬────┘
     │                                                 │
     │                                            ┌────▼────┐
     │                                            │Calculate│
     │                                            │  Total  │
     │                                            │  Price  │
     │                                            └────┬────┘
     │                                                 │
     │                                            ┌────▼────┐
     │                                            │  Apply  │
     │                                            │ Discount│
     │                                            └────┬────┘
     │                                                 │
     │                                            ┌────▼────┐
     │                                            │ Create  │
     │                                            │  Order  │
     │                                            │ Record  │
     │                                            └────┬────┘
     │                                                 │
     │                                            ┌────▼────┐
     │                                            │Increment│
     │                                            │ Coupon  │
     │                                            │  Usage  │
     │                                            └────┬────┘
     │                                                 │
     │                                            ┌────▼────┐
     │                                            │ Trigger │
     │                                            │ Webhook │
     │                                            │  ORDER_ │
     │                                            │ CREATED │
     │                                            └────┬────┘
     │  201 Created                                    │
     │<────────────────────────────────────────────────┤
     │  { order_id, total_amount, status, ... }       │
     │                                                 │
     │  4. Update order status                         │
     ├────────────────────────────────────────────────>│
     │  PUT /api/v1/orders/{order_id}                  │
     │  { status: "SHIPPED" }                          │
     │                                            ┌────▼────┐
     │                                            │ Update  │
     │                                            │  Order  │
     │                                            │  Status │
     │                                            └────┬────┘
     │                                                 │
     │                                            ┌────▼────┐
     │                                            │ Trigger │
     │                                            │ Webhook │
     │                                            │  ORDER_ │
     │                                            │ UPDATED │
     │                                            └────┬────┘
     │  200 OK                                         │
     │<────────────────────────────────────────────────┤
     │  { order with updated status }                  │
     │                                                 │
```

### 4. Webhook Delivery Flow

```
┌──────────┐                ┌─────────┐                ┌──────────┐
│  Event   │                │  Server │                │ External │
│ Trigger  │                │         │                │ Endpoint │
└────┬─────┘                └────┬────┘                └────┬─────┘
     │                           │                          │
     │  Event occurs             │                          │
     │  (e.g., ORDER_CREATED)    │                          │
     ├──────────────────────────>│                          │
     │                           │                          │
     │                      ┌────▼────┐                     │
     │                      │  Find   │                     │
     │                      │ Active  │                     │
     │                      │Webhooks │                     │
     │                      │for Event│                     │
     │                      └────┬────┘                     │
     │                           │                          │
     │                      ┌────▼────┐                     │
     │                      │ Create  │                     │
     │                      │Delivery │                     │
     │                      │ Record  │                     │
     │                      └────┬────┘                     │
     │                           │                          │
     │                      ┌────▼────┐                     │
     │                      │Generate │                     │
     │                      │  HMAC   │                     │
     │                      │Signature│                     │
     │                      └────┬────┘                     │
     │                           │                          │
     │                           │  POST {webhook_url}      │
     │                           │  X-Webhook-Signature     │
     │                           ├─────────────────────────>│
     │                           │  { event_type, data }    │
     │                           │                          │
     │                           │                     ┌────▼────┐
     │                           │                     │ Verify  │
     │                           │                     │Signature│
     │                           │                     └────┬────┘
     │                           │                          │
     │                           │                     ┌────▼────┐
     │                           │                     │ Process │
     │                           │                     │  Event  │
     │                           │                     └────┬────┘
     │                           │  200 OK                  │
     │                           │<─────────────────────────┤
     │                           │                          │
     │                      ┌────▼────┐                     │
     │                      │  Mark   │                     │
     │                      │Delivery │                     │
     │                      │SUCCESS  │                     │
     │                      └────┬────┘                     │
     │                           │                          │
     │                           │  (If failed)             │
     │                      ┌────▼────┐                     │
     │                      │Schedule │                     │
     │                      │  Retry  │                     │
     │                      │ with    │                     │
     │                      │Backoff  │                     │
     │                      └─────────┘                     │
     │                           │                          │
```

---

## ✅ Implementation Summary

### Phase 1: Foundation ✅ COMPLETED
- FastAPI application setup
- Database models and migrations
- JWT authentication
- Core API structure

### Phase 2: Multi-Tenancy ✅ COMPLETED
- Super Admin routes (10 endpoints)
- Agency Admin routes (6 endpoints)
- User management (6 endpoints)
- Hierarchical tenant isolation

### Phase 3: E-Commerce Core ✅ COMPLETED
- Product management (6 endpoints)
- Order processing (5 endpoints)
- Customer management (6 endpoints)
- Inventory tracking

### Phase 4: Shopping & Engagement ✅ COMPLETED
- Shopping cart system (5 endpoints)
- Coupon management (6 endpoints)
- Product reviews (9 endpoints)
- Review moderation

### Phase 5: Advanced Features ✅ COMPLETED
- Webhook system (8 endpoints)
- Audit logging (4 endpoints)
- Event notifications
- Compliance tracking

### Statistics
- **Total Endpoints:** 82 (80 API + 2 health checks)
- **Database Tables:** 19
- **Models:** 14
- **Services:** 12
- **Routers:** 12
- **Schemas:** 15+
- **Lines of Code:** ~8,500+

---

## 🔧 Component Details

### Core Infrastructure

**Files:**
- `app/main.py` - FastAPI application entry point
- `app/core/config.py` - Environment configuration
- `app/core/database.py` - Database connection
- `app/core/security.py` - JWT & password utilities
- `app/core/dependencies.py` - Dependency injection

**Features:**
- CORS middleware configured
- Environment-based configuration
- Database connection pooling
- Health check endpoints

### Authentication System

**Components:**
- JWT token generation (access + refresh)
- Password hashing with bcrypt
- Token expiration and refresh
- Role-based access control

**Endpoints:**
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Token refresh
- `GET /api/v1/auth/me` - Current user profile

### Database Models

| Model | Tables | Purpose |
|-------|--------|---------|
| User | users | Authentication & role management |
| Agency | agencies | Agency management |
| SubscriptionPlan | subscription_plans | Pricing tiers |
| Ecommerce | ecommerce | E-commerce stores |
| Product | products | Product catalog |
| Inventory | inventory | Stock management |
| Order | orders, order_items | Order processing |
| Customer | customers | Customer management |
| Cart | carts, cart_items | Shopping cart |
| Coupon | coupons | Discount codes |
| Webhook | webhooks, webhook_deliveries | Event notifications |
| ProductReview | product_reviews | Customer reviews |
| AuditLog | audit_logs | Change tracking |
| TokenBlacklist | token_blacklist | Revoked JWT tokens |

### Service Layer

Each service handles business logic for its domain:

- **AuthService** - Authentication logic
- **UserService** - User CRUD operations
- **ProductService** - Product management
- **OrderService** - Order processing
- **CustomerService** - Customer management
- **CartService** - Shopping cart operations
- **CouponService** - Discount management
- **WebhookService** - Event notifications
- **ReviewService** - Review management
- **AuditLogService** - Audit trail
- **SubscriptionService** - Plan management

---

## 📡 API Endpoints

### Endpoint Summary by Category

| Category | Count | Base Path |
|----------|-------|-----------|
| Health | 2 | `/` |
| Authentication | 7 | `/api/v1/auth` |
| Super Admin | 10 | `/api/v1/admin` |
| Agency Admin | 6 | `/api/v1/agencies` |
| Users | 6 | `/api/v1/users` |
| Products | 6 | `/api/v1/products` |
| Orders | 5 | `/api/v1/orders` |
| Customers | 6 | `/api/v1/customers` |
| Cart | 5 | `/api/v1/cart` |
| Coupons | 6 | `/api/v1/coupons` |
| Webhooks | 8 | `/api/v1/webhooks` |
| Reviews | 9 | `/api/v1/reviews` |
| Audit Logs | 4 | `/api/v1/audit-logs` |
| **TOTAL** | **80** | |

---

### Detailed Endpoint Documentation

#### 🏥 Health Check Routes (2)
- `GET /` - Root health check
- `GET /health` - Detailed health check with database status

---

#### 🔐 Authentication Routes (7)
**Base Path:** `/api/v1/auth`

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| POST | `/register` | Register new user | Public |
| POST | `/login` | Login with email/password | Public |
| POST | `/login/form` | Login with form data | Public |
| POST | `/refresh` | Refresh access token | Public |
| GET | `/me` | Get current user profile | Authenticated |
| POST | `/logout` | Logout user (blacklist token) | Authenticated |
| POST | `/extend-session` | Extend session and get new tokens | Authenticated |

**Session Management:**
- Tokens are blacklisted on logout for security
- Automatic logout after 30 minutes of inactivity
- Session extension resets the inactivity timer
- Activity tracking on every authenticated request

---

#### 👑 Super Admin Routes (10)
**Base Path:** `/api/v1/admin`

**Subscription Plans (5)**

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/subscription-plans` | Create subscription plan |
| GET | `/subscription-plans` | List all subscription plans |
| GET | `/subscription-plans/{plan_id}` | Get plan details |
| PUT | `/subscription-plans/{plan_id}` | Update plan |
| DELETE | `/subscription-plans/{plan_id}` | Delete plan |

**Agencies (5)**

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/agencies` | Create agency |
| GET | `/agencies` | List all agencies |
| GET | `/agencies/{agency_id}` | Get agency details |
| PUT | `/agencies/{agency_id}` | Update agency |
| DELETE | `/agencies/{agency_id}` | Delete agency |

---

#### 🏢 Agency Admin Routes (6)
**Base Path:** `/api/v1/agencies`

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/ecommerce` | Create e-commerce tenant |
| GET | `/ecommerce` | List all e-commerce tenants |
| GET | `/ecommerce/{ecommerce_id}` | Get tenant details |
| PUT | `/ecommerce/{ecommerce_id}` | Update tenant |
| DELETE | `/ecommerce/{ecommerce_id}` | Delete tenant |
| GET | `/ecommerce/{ecommerce_id}/stats` | Get tenant statistics |

---

#### 👥 User Management Routes (6)
**Base Path:** `/api/v1/users`

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `` | Create user |
| GET | `` | List users |
| GET | `/me` | Get current user profile |
| GET | `/{user_id}` | Get user details |
| PUT | `/{user_id}` | Update user |
| DELETE | `/{user_id}` | Delete user |

---

#### 📦 Product Routes (6)
**Base Path:** `/api/v1/products`

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `` | Create product with inventory |
| GET | `` | List products (with filters) |
| GET | `/{product_id}` | Get product details |
| PUT | `/{product_id}` | Update product |
| DELETE | `/{product_id}` | Delete product |
| PUT | `/{product_id}/inventory` | Update inventory quantity |

**Query Filters:** category, is_active, min_price, max_price

---

#### 📋 Order Routes (5)
**Base Path:** `/api/v1/orders`

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `` | Create order |
| GET | `` | List orders (with filters) |
| GET | `/{order_id}` | Get order details |
| PUT | `/{order_id}` | Update order status |
| POST | `/{order_id}/cancel` | Cancel order |

**Query Filters:** status, customer_id

---

#### 👤 Customer Routes (6)
**Base Path:** `/api/v1/customers`

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `` | Create customer |
| GET | `` | List customers |
| GET | `/{customer_id}` | Get customer details |
| PUT | `/{customer_id}` | Update customer |
| DELETE | `/{customer_id}` | Delete customer |
| GET | `/{customer_id}/stats` | Get customer statistics |

---

#### 🛒 Cart Routes (5)
**Base Path:** `/api/v1/cart`

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `` | Create new cart |
| GET | `/{cart_id}` | Get cart details |
| POST | `/{cart_id}/items` | Add item to cart |
| PUT | `/{cart_id}/items/{item_id}` | Update cart item quantity |
| DELETE | `/{cart_id}/items/{item_id}` | Remove item from cart |

---

#### 🎫 Coupon Routes (6)
**Base Path:** `/api/v1/coupons`

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `` | Create coupon |
| GET | `` | List all coupons |
| GET | `/{coupon_id}` | Get coupon details |
| PUT | `/{coupon_id}` | Update coupon |
| DELETE | `/{coupon_id}` | Delete coupon |
| POST | `/validate/{code}` | Validate coupon code |

**Coupon Types:** Percentage, Fixed Amount, Free Shipping  
**Features:** Usage limits, minimum purchase requirements, validity periods, active/inactive status

---

#### 🔔 Webhook Routes (8)
**Base Path:** `/api/v1/webhooks`

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `` | Create webhook |
| GET | `` | List all webhooks |
| GET | `/{webhook_id}` | Get webhook details |
| PUT | `/{webhook_id}` | Update webhook |
| DELETE | `/{webhook_id}` | Delete webhook |
| POST | `/{webhook_id}/regenerate-secret` | Regenerate webhook secret |
| POST | `/{webhook_id}/test` | Test webhook delivery |
| GET | `/{webhook_id}/deliveries` | Get delivery history |

**Event Types:** ORDER_CREATED, ORDER_UPDATED, ORDER_CANCELLED, PAYMENT_SUCCESS, PAYMENT_FAILED, PRODUCT_CREATED, PRODUCT_UPDATED, INVENTORY_LOW, CUSTOMER_CREATED  
**Security:** HMAC-SHA256 signatures, secret key per webhook  
**Reliability:** Automatic retry with exponential backoff, delivery history tracking

---

#### ⭐ Review Routes (9)
**Base Path:** `/api/v1/reviews`

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `` | Create product review |
| GET | `/product/{product_id}` | Get product reviews |
| GET | `/product/{product_id}/stats` | Get review statistics |
| GET | `/my-reviews` | Get current user's reviews |
| GET | `/{review_id}` | Get review details |
| PUT | `/{review_id}` | Update review |
| DELETE | `/{review_id}` | Delete review |
| PATCH | `/{review_id}/moderate` | Moderate review (admin only) |
| POST | `/{review_id}/helpful` | Mark review as helpful |

**Features:** 1-5 star ratings, optional title & comment, image uploads, verified purchase badge, moderation system, helpful voting

---

#### 📝 Audit Log Routes (4)
**Base Path:** `/api/v1/audit-logs`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `` | List audit logs (with filters) |
| GET | `/my-activity` | Get current user's activity |
| GET | `/{log_id}` | Get audit log details |
| GET | `/resource/{resource_type}/{resource_id}` | Get resource history |

**Query Filters:** user_id, ecommerce_id, agency_id, action, resource_type, resource_id, date_range  
**Tracked Data:** User actions, resource changes (old/new values), IP address, user agent, timestamps

---

### Access Control Matrix

| Endpoint Category | Public | User | E-commerce | Agency Admin | Super Admin |
|-------------------|--------|------|------------|--------------|-------------|
| Health | ✅ | ✅ | ✅ | ✅ | ✅ |
| Auth (register/login) | ✅ | ✅ | ✅ | ✅ | ✅ |
| Auth (me) | ❌ | ✅ | ✅ | ✅ | ✅ |
| Super Admin | ❌ | ❌ | ❌ | ❌ | ✅ |
| Agency Admin | ❌ | ❌ | ❌ | ✅ | ✅ |
| Users | ❌ | ❌ | ✅ | ✅ | ✅ |
| Products | ❌ | ❌ | ✅ | ✅ | ✅ |
| Orders | ❌ | ❌ | ✅ | ✅ | ✅ |
| Customers | ❌ | ❌ | ✅ | ✅ | ✅ |
| Cart | ❌ | ❌ | ✅ | ✅ | ✅ |
| Coupons | ❌ | ❌ | ✅ | ✅ | ✅ |
| Webhooks | ❌ | ❌ | ✅ | ✅ | ✅ |
| Reviews (read) | ✅ | ✅ | ✅ | ✅ | ✅ |
| Reviews (write) | ❌ | ❌ | ✅ | ✅ | ✅ |
| Reviews (moderate) | ❌ | ❌ | ❌ | ✅ | ✅ |
| Audit Logs | ❌ | ❌ | ❌ | ✅ | ✅ |

---

## 🗄️ Database Schema

### Entity Relationship Diagram

```
┌─────────────────┐
│ SubscriptionPlan│
│─────────────────│
│ id (PK)         │
│ name            │
│ price           │
│ features        │
└────────┬────────┘
         │
         │ 1:N
         │
┌────────▼────────┐
│     Agency      │
│─────────────────│
│ id (PK)         │
│ subscription_id │───────┐
│ name            │       │
│ status          │       │
│ max_ecommerce   │       │
└────────┬────────┘       │
         │                │
         │ 1:N            │
         │                │
┌────────▼────────┐       │
│   Ecommerce     │       │
│─────────────────│       │
│ id (PK)         │       │
│ agency_id (FK)  │───────┘
│ name            │
│ domain          │
│ api_key         │
└────────┬────────┘
         │
         ├──────────────┬──────────────┬──────────────┬──────────────┬──────────────┐
         │              │              │              │              │              │
         │ 1:N          │ 1:N          │ 1:N          │ 1:N          │ 1:N          │ 1:N
         │              │              │              │              │              │
┌────────▼────┐ ┌───────▼──────┐ ┌────▼──────┐ ┌────▼──────┐ ┌────▼──────┐ ┌────▼──────┐
│   Product   │ │    Order     │ │  Customer │ │    Cart   │ │   Coupon  │ │  Webhook  │
│─────────────│ │──────────────│ │───────────│ │───────────│ │───────────│ │───────────│
│ id (PK)     │ │ id (PK)      │ │ id (PK)   │ │ id (PK)   │ │ id (PK)   │ │ id (PK)   │
│ ecomm_id(FK)│ │ ecomm_id(FK) │ │ ecomm_id  │ │ ecomm_id  │ │ ecomm_id  │ │ ecomm_id  │
│ name        │ │ customer_id  │ │ email     │ │ customer  │ │ code      │ │ url       │
│ sku         │ │ status       │ │ name      │ │ status    │ │ discount  │ │ events[]  │
│ price       │ │ total_amount │ │ addresses │ └─────┬─────┘ │ valid_from│ │ secret    │
└──────┬──────┘ └──────┬───────┘ └─────┬─────┘       │       │ usage_cnt │ └─────┬─────┘
       │               │               │             │       └───────────┘       │
       │ 1:1           │ 1:N           │ 1:N         │ 1:N                      │ 1:N
       │               │               │             │                          │
┌──────▼──────┐ ┌──────▼──────┐ ┌──────▼─────┐ ┌───▼──────┐          ┌────────▼─────────┐
│  Inventory  │ │  OrderItem  │ │   Review   │ │ CartItem │          │ WebhookDelivery  │
│─────────────│ │─────────────│ │────────────│ │──────────│          │──────────────────│
│ id (PK)     │ │ id (PK)     │ │ id (PK)    │ │ id (PK)  │          │ id (PK)          │
│ product_id  │ │ order_id    │ │ product_id │ │ cart_id  │          │ webhook_id (FK)  │
│ quantity    │ │ product_id  │ │ customer_id│ │ product  │          │ event_type       │
│ reserved    │ │ quantity    │ │ rating     │ │ quantity │          │ status           │
└─────────────┘ │ price       │ │ comment    │ │ price    │          │ http_status      │
                └─────────────┘ │ is_approved│ └──────────┘          │ attempt_count    │
                                └────────────┘                        └──────────────────┘

┌──────────────┐
│   AuditLog   │
│──────────────│
│ id (PK)      │
│ user_id      │
│ action       │
│ resource_type│
│ resource_id  │
│ old_values   │
│ new_values   │
│ ip_address   │
│ created_at   │
└──────────────┘

┌─────────┐
│   User  │
│─────────│
│ id (PK) │
│ email   │
│ password│
│ role    │
│ agency  │
│ ecomm_id│
└─────────┘
```

### Table Relationships

**One-to-Many:**
- Agency → Ecommerce (1:N)
- Ecommerce → Products (1:N)
- Ecommerce → Orders (1:N)
- Ecommerce → Customers (1:N)
- Ecommerce → Carts (1:N)
- Ecommerce → Coupons (1:N)
- Ecommerce → Webhooks (1:N)
- Product → Reviews (1:N)
- Customer → Reviews (1:N)
- Order → OrderItems (1:N)
- Cart → CartItems (1:N)
- Webhook → WebhookDeliveries (1:N)

**One-to-One:**
- Product ↔ Inventory (1:1)

---

## 🔐 Authentication Flow

### JWT Token Structure

```json
{
  "access_token": {
    "sub": "user_email@example.com",
    "exp": 1703097600,
    "iat": 1703094000,
    "type": "access"
  },
  "refresh_token": {
    "sub": "user_email@example.com",
    "exp": 1703529600,
    "iat": 1703094000,
    "type": "refresh"
  }
}
```

### Token Lifecycle

1. **Registration/Login** → Generate access_token (60 min) + refresh_token (7 days)
2. **API Request** → Include `Authorization: Bearer {access_token}`
3. **Token Validation** → Verify signature, expiration, user exists
4. **Token Expired** → Use refresh_token to get new access_token
5. **Refresh Token Expired** → User must login again

### Password Security

- **Hashing Algorithm:** bcrypt with cost factor 12
- **Salt:** Automatically generated per password
- **Verification:** Constant-time comparison

---

## 🏢 Multi-Tenancy Implementation

### Tenant Isolation Strategy

**Shared Database with Row-Level Isolation**

```python
# Automatic tenant filtering via dependency injection
async def require_ecommerce_context(
    current_user: User = Depends(get_current_user)
) -> UUID:
    if current_user.role == UserRole.SUPER_ADMIN:
        raise HTTPException(403, "Super admin cannot access tenant data")
    
    if not current_user.ecommerce_id:
        raise HTTPException(400, "User must be associated with ecommerce")
    
    return current_user.ecommerce_id

# Usage in routes
@router.get("/products")
async def get_products(
    ecommerce_id: UUID = Depends(require_ecommerce_context),
    db: Session = Depends(get_db)
):
    # All queries automatically filtered by ecommerce_id
    products = ProductService.get_products(db, ecommerce_id)
    return products
```

### Tenant Data Flow

```
Request → Auth Token → Extract User → Get User's ecommerce_id → 
Filter DB Query → Return Only Tenant's Data
```

### Benefits
- ✅ Single database instance
- ✅ Automatic tenant isolation
- ✅ Cost-effective scaling
- ✅ Easy backups and migrations
- ✅ Shared resources optimization

---

## 📊 Code Statistics

### File Count by Category

| Category | Files | Purpose |
|----------|-------|---------|
| Models | 13 | Database entities |
| Routers | 12 | API endpoints |
| Services | 12 | Business logic |
| Schemas | 15 | Data validation |
| Core | 4 | Infrastructure |
| Migrations | 2 | Database versions |
| Scripts | 1 | Utilities |

### Code Metrics

```
Total Lines of Code: ~8,000+
├── Models:          ~1,500
├── Services:        ~2,000
├── Routers:         ~2,500
├── Schemas:         ~1,200
├── Core:            ~400
└── Other:           ~400
```

### Dependencies

**Core:**
- fastapi (0.104.1)
- uvicorn (0.24.0)
- sqlalchemy (2.0.23)
- alembic (1.13.0)
- pydantic (2.12.5)

**Security:**
- python-jose[cryptography] (3.3.0)
- passlib[bcrypt] (1.7.4)
- bcrypt (4.3.0)

**Database:**
- psycopg2-binary (2.9.9)

**Utilities:**
- python-multipart (0.0.6)
- email-validator (2.3.0)
- httpx (0.28.1)

---

## 🔒 Quality & Security

### Security Features

✅ **Authentication:**
- JWT tokens with expiration
- Refresh token mechanism
- Secure password hashing (bcrypt)

✅ **Authorization:**
- Role-based access control (RBAC)
- Hierarchical permissions
- Tenant isolation

✅ **Data Protection:**
- SQL injection prevention (SQLAlchemy ORM)
- XSS protection (Pydantic validation)
- CORS configuration
- Environment-based secrets

✅ **Audit Trail:**
- Complete change tracking
- User action logging
- IP address recording
- Resource modification history

### Code Quality

✅ **Type Safety:**
- Python 3.12 type hints
- Pydantic v2 validation
- SQLAlchemy 2.0 typed models

✅ **Error Handling:**
- Custom HTTP exceptions
- Validation error messages
- Database error handling

✅ **Documentation:**
- OpenAPI/Swagger UI
- ReDoc alternative docs
- Inline code comments
- Comprehensive README

---

## 🚀 Running the Application

### Quick Start

```bash
# 1. Install dependencies
poetry install

# 2. Configure environment
cp .env.example .env
# Edit .env with your settings

# 3. Setup database
createdb -U postgres MSuite
poetry run alembic upgrade head

# 4. Seed initial data (optional)
poetry run python scripts/seed_db.py

# 5. Start server
poetry run uvicorn app.main:app --reload --port 8000
```

### Access Points

- **API Documentation:** http://localhost:8000/docs
- **Alternative Docs:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health
- **OpenAPI Schema:** http://localhost:8000/openapi.json

### Default Credentials

After seeding:
- **Email:** admin@msuite.com
- **Password:** Admin@123
- **Role:** SUPER_ADMIN

---

## 🧪 Testing Guide

### Manual Testing via Swagger UI

1. **Navigate to:** http://localhost:8000/docs
2. **Register/Login** to get access token
3. **Authorize** by clicking lock icon and pasting token
4. **Test endpoints** in order:
   - Create subscription plan
   - Create agency
   - Create e-commerce store
   - Create products
   - Create orders
   - Test all features

### Example API Workflow

```bash
# 1. Register user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123",
    "full_name": "Test User",
    "role": "SUPER_ADMIN"
  }'

# 2. Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123"
  }'

# Save the access_token from response

# 3. Create subscription plan
curl -X POST http://localhost:8000/api/v1/admin/subscription-plans \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Basic Plan",
    "price": 29.99,
    "billing_cycle": "MONTHLY",
    "max_ecommerce": 5
  }'

# 4. Create agency
curl -X POST http://localhost:8000/api/v1/admin/agencies \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Agency",
    "subscription_plan_id": "{plan_id}",
    "contact_email": "contact@agency.com"
  }'
```

---

## 🎯 Future Enhancements

### Phase 6: Analytics & Integrations (Planned)

**Dashboard & Reporting:**
- Revenue analytics dashboard
- Sales reports and charts
- Customer behavior analytics
- Product performance metrics
- Real-time statistics

**Payment Integration:**
- Stripe integration
- PayPal integration
- Multiple currency support
- Automatic invoice generation

**Communication:**
- Email notification system
- SMS notifications (Twilio)
- Order confirmation emails
- Shipping update emails

**Advanced Features:**
- Advanced product search (Elasticsearch)
- Product recommendations
- Abandoned cart recovery
- Loyalty points system
- Gift cards and vouchers

**Performance:**
- Redis caching
- Rate limiting per tenant
- API usage metrics
- Query optimization

**DevOps:**
- Docker containerization
- CI/CD pipeline
- Automated testing
- Monitoring and logging

---

## 📚 Additional Documentation

- **[README.md](README.md)** - Project overview and quick start
- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Detailed setup instructions
- **[ROUTES_SUMMARY.md](ROUTES_SUMMARY.md)** - Complete API reference
- **[API Documentation](http://localhost:8000/docs)** - Interactive Swagger UI

---

## 🎓 Key Learnings

### Architecture Decisions

1. **Shared Database Multi-Tenancy**
   - Pros: Cost-effective, easy management
   - Cons: Requires careful query filtering
   - Mitigation: Dependency injection for automatic filtering

2. **JWT Authentication**
   - Pros: Stateless, scalable
   - Cons: Cannot revoke before expiration
   - Mitigation: Short access token lifetime + refresh tokens

3. **Service Layer Pattern**
   - Pros: Separation of concerns, testable
   - Cons: Additional abstraction
   - Benefit: Clean business logic separation

4. **Synchronous SQLAlchemy**
   - Choice: Used sync instead of async for simplicity
   - Trade-off: Slightly lower concurrency vs easier debugging
   - Result: Good performance for current scale

---

## ✅ Quality Checklist

- ✅ All API endpoints documented
- ✅ Authentication and authorization implemented
- ✅ Database migrations working
- ✅ Multi-tenancy isolation verified
- ✅ Error handling in place
- ✅ Input validation with Pydantic
- ✅ CORS configured
- ✅ Environment variables used for secrets
- ✅ Relationship cascades configured
- ✅ Indexes on foreign keys
- ✅ Health check endpoints
- ✅ Swagger UI documentation
- ✅ README and setup guide
- ✅ Git repository initialized

---

## 🎉 Conclusion

**MSuite is production-ready!**

The platform provides a complete Backend-as-a-Service solution for multi-tenant e-commerce operations with:

- ✅ **80 API endpoints** covering all e-commerce needs
- ✅ **18 database tables** with proper relationships
- ✅ **Secure authentication** with JWT and bcrypt
- ✅ **Multi-tenant isolation** via hierarchical architecture
- ✅ **Advanced features** including webhooks, coupons, reviews, audit logs
- ✅ **Production-ready** code with proper error handling and validation
- ✅ **Well-documented** with comprehensive guides and API docs

The foundation is solid and ready for scaling to serve multiple agencies and their e-commerce clients!

---

**Built with ❤️ using FastAPI, PostgreSQL, and SQLAlchemy**

*Last Updated: December 20, 2025*
