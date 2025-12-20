# API Routes Summary

## 📑 Table of Contents

- [Total Routes](#total-routes-91-endpoints)
- [Health Check Routes (2)](#health-check-routes-2)
- [Authentication Routes (7)](#authentication-routes-7)
- [Super Admin Routes (10)](#super-admin-routes-10)
- [Agency Admin Routes (7)](#agency-admin-routes-7)
- [User Management Routes (6)](#user-management-routes-6)
- [Product Routes (6)](#product-routes-6)
- [Order Routes (5)](#order-routes-5)
- [Customer Routes (6)](#customer-routes-6)
- [Cart Routes (5)](#cart-routes-5)
- [Coupon Routes (6)](#coupon-routes-6)
- [Webhook Routes (8)](#webhook-routes-8)
- [Review Routes (9)](#review-routes-9)
- [Refund Routes (6)](#refund-routes-6)
- [Audit Log Routes (4)](#audit-log-routes-4)
- [Route Summary by Category](#route-summary-by-category)
- [Access Control](#access-control)
- [Multi-Tenancy](#multi-tenancy)

---

## Total Routes: 91 endpoints

**Breakdown:**
- Health: 2
- Auth: 7
- Super Admin: 10
- Agency Admin: 7 (including API key rotation)
- Users: 6
- Products: 6
- Orders: 5
- Customers: 6
- Cart: 5
- Coupons: 6
- Webhooks: 8
- Reviews: 9
- **Refunds: 6** ✨ NEW
- Audit Logs: 4

---

## Health Check Routes (2)
- `GET /` - Root health check
- `GET /health` - Detailed health check

---

## Authentication Routes (7)
**Base Path:** `/api/v1/auth`

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/register` | Register new user |
| POST | `/login` | Login with email/password |
| POST | `/login/form` | Login with form data |
| POST | `/refresh` | Refresh access token |
| GET | `/me` | Get current user profile |
| POST | `/logout` | Logout user (blacklist token) |
| POST | `/extend-session` | Extend session and get new tokens |

---

## Super Admin Routes (10)
**Base Path:** `/api/v1/admin`

### Subscription Plans (5)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/subscription-plans` | Create subscription plan |
| GET | `/subscription-plans` | List all subscription plans |
| GET | `/subscription-plans/{plan_id}` | Get plan details |
| PUT | `/subscription-plans/{plan_id}` | Update plan |
| DELETE | `/subscription-plans/{plan_id}` | Delete plan |

### Agencies (5)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/agencies` | Create agency |
| GET | `/agencies` | List all agencies |
| GET | `/agencies/{agency_id}` | Get agency details |
| PUT | `/agencies/{agency_id}` | Update agency |
| DELETE | `/agencies/{agency_id}` | Delete agency |

---

## Agency Admin Routes (7)
**Base Path:** `/api/v1/agencies`

### E-commerce Tenants (7)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/ecommerce` | Create e-commerce tenant |
| GET | `/ecommerce` | List all e-commerce tenants |
| GET | `/ecommerce/{ecommerce_id}` | Get tenant details |
| PUT | `/ecommerce/{ecommerce_id}` | Update tenant |
| DELETE | `/ecommerce/{ecommerce_id}` | Delete tenant |
| GET | `/ecommerce/{ecommerce_id}/stats` | Get tenant statistics |
| **POST** | **`/ecommerce/{ecommerce_id}/regenerate-api-key`** | **Rotate API key** ✨ NEW
| GET | `/ecommerce/{ecommerce_id}/stats` | Get tenant statistics |

---

## User Management Routes (6)
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

## Product Routes (6)
**Base Path:** `/api/v1/products`

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `` | Create product with inventory |
| GET | `` | List products (with filters) |
| GET | `/{product_id}` | Get product details |
| PUT | `/{product_id}` | Update product |
| DELETE | `/{product_id}` | Delete product |
| PUT | `/{product_id}/inventory` | Update inventory quantity |

**Filters:** category, is_active, min_price, max_price

---

## Order Routes (5)
**Base Path:** `/api/v1/orders`

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `` | Create order |
| GET | `` | List orders (with filters) |
| GET | `/{order_id}` | Get order details |
| PUT | `/{order_id}` | Update order status |
| POST | `/{order_id}/cancel` | Cancel order |

**Filters:** status, customer_id

---

## Customer Routes (6)
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

## Cart Routes (5)
**Base Path:** `/api/v1/cart`

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `` | Create new cart |
| GET | `/{cart_id}` | Get cart details |
| POST | `/{cart_id}/items` | Add item to cart |
| PUT | `/{cart_id}/items/{item_id}` | Update cart item quantity |
| DELETE | `/{cart_id}/items/{item_id}` | Remove item from cart |

---

## Coupon Routes (6)
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

---

## Webhook Routes (8)
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

---

## Review Routes (9)
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
| PATCH | `/{review_id}/moderate` | Moderate review (admin) |
| POST | `/{review_id}/helpful` | Mark review as helpful |

---

## Refund Routes (6)
**Base Path:** `/api/v1/refunds`

| Method | Endpoint | Description |
|--------|----------|-------------|
| **POST** | **``** | **Create refund request** ✨ NEW |
| **GET** | **``** | **List refunds (with status filter)** ✨ NEW |
| **GET** | **`/{refund_id}`** | **Get refund details** ✨ NEW |
| **POST** | **`/{refund_id}/approve`** | **Approve/reject refund (admin)** ✨ NEW |
| **POST** | **`/{refund_id}/process`** | **Process refund transaction** ✨ NEW |
| **PATCH** | **`/{refund_id}`** | **Update refund details (admin)** ✨ NEW |

**Features:**
- Complete refund workflow: REQUESTED → APPROVED → PROCESSING → COMPLETED
- Inventory return on refund completion
- Transaction tracking with payment gateway IDs
- Partial refund support
- Admin approval/rejection with notes
- Multiple refund reasons (defective, wrong item, damaged, etc.)

---

## Audit Log Routes (4)
**Base Path:** `/api/v1/audit-logs`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `` | List audit logs (with filters) |
| GET | `/my-activity` | Get current user's activity |
| GET | `/{log_id}` | Get audit log details |
| GET | `/resource/{resource_type}/{resource_id}` | Get resource history |

**Filters:** user_id, ecommerce_id, agency_id, action, resource_type, resource_id, date_range

---

## Route Summary by Category

| Category | Routes | Description |
|----------|--------|-------------|
| Health | 2 | System health checks |
| Authentication | 7 | User authentication & tokens |
| Super Admin | 10 | System-level management |
| Agency Admin | 7 | Multi-tenant management + API key rotation |
| Users | 6 | User CRUD operations |
| Products | 6 | Product & inventory management |
| Orders | 5 | Order processing |
| Customers | 6 | Customer management |
| Cart | 5 | Shopping cart operations |
| Coupons | 6 | Discount code management |
| Webhooks | 8 | Event notification system |
| Reviews | 9 | Product reviews & ratings |
| **Refunds** | **6** | **Refund & return management** ✨ NEW |
| Audit Logs | 4 | System audit trail |
| **TOTAL** | **91** | **All endpoints** |

---

## Access Control

### Public Routes
- Health check endpoints
- Authentication endpoints (register, login, refresh)

### Super Admin Only
- All `/admin/*` routes
- Subscription plan management
- Agency management

### Agency Admin Only
- E-commerce tenant management
- User management within agency
- View agency statistics

### E-commerce Context Required
- All product routes
- All order routes
- All customer routes
- All cart routes
- All coupon routes
- All webhook routes
- All review routes
- Tenant-scoped operations

---

## Multi-Tenancy

The application implements **shared database multi-tenancy** with tenant isolation at the data level:

1. **Super Admin** - Global system access
2. **Agency Admin** - Access to their agency and all e-commerce tenants under it
3. **Ecommerce Users** - Access only to their e-commerce tenant data

All e-commerce operations (products, orders, customers) are automatically filtered by `ecommerce_id` through dependency injection.
