# API Documentation

Complete API reference for MSuite - Multi-Tenant E-Commerce Backend-as-a-Service

---

## 📑 Table of Contents

- [Overview](#overview)
- [Authentication](#authentication)
- [Base URL](#base-url)
- [Response Format](#response-format)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [API Endpoints](#api-endpoints)
  - [Health Check](#health-check)
  - [Authentication](#authentication-endpoints)
  - [User Management](#user-management)
  - [Super Admin](#super-admin)
  - [Agency Admin](#agency-admin)
  - [Products](#products)
  - [Orders](#orders)
  - [Customers](#customers)
  - [Shopping Cart](#shopping-cart)
  - [Coupons](#coupons)
  - [Webhooks](#webhooks)
  - [Reviews](#reviews)
  - [Refunds](#refunds)
  - [Audit Logs](#audit-logs)

---

## Overview

MSuite provides a RESTful API with **91 endpoints** for managing multi-tenant e-commerce operations.

### Key Features
- **RESTful Design** - Standard HTTP methods (GET, POST, PUT, PATCH, DELETE)
- **JSON Format** - All requests and responses use JSON
- **JWT Authentication** - Secure token-based authentication
- **API Key Authentication** - For e-commerce storefronts
- **Role-Based Access** - Three-tier permission system
- **Comprehensive Documentation** - OpenAPI/Swagger specs
- **Complete Operations** - Including refunds, returns, and billing

### Interactive Documentation
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## Authentication

MSuite uses **JWT (JSON Web Tokens)** for authentication.

### Authentication Flow

1. **Register** or **Login** to get access and refresh tokens
2. Include the access token in the `Authorization` header for all requests
3. Refresh the access token when it expires using the refresh token

### Headers

```http
Authorization: Bearer <access_token>
Content-Type: application/json
```

### Token Types

| Token | Purpose | Expiration |
|-------|---------|------------|
| **Access Token** | API authentication | 60 minutes |
| **Refresh Token** | Renew access token | 7 days |

### Session Management

- **Inactivity Timeout:** 30 minutes
- **Session Extension:** Use `/api/v1/auth/extend-session`
- **Logout:** Tokens are blacklisted on logout

---

## Base URL

```
Development: http://localhost:8000
Production: https://api.yourdomain.com
```

All API endpoints are prefixed with `/api/v1` except health checks.

---

## Response Format

### Success Response

```json
{
  "id": "uuid",
  "name": "Product Name",
  "price": 29.99,
  "created_at": "2025-12-20T10:00:00Z"
}
```

### List Response

```json
[
  {
    "id": "uuid-1",
    "name": "Item 1"
  },
  {
    "id": "uuid-2",
    "name": "Item 2"
  }
]
```

---

## Error Handling

### Error Response Format

```json
{
  "detail": "Error message"
}
```

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| **200** | OK | Request successful |
| **201** | Created | Resource created |
| **400** | Bad Request | Invalid input |
| **401** | Unauthorized | Authentication required |
| **403** | Forbidden | Insufficient permissions |
| **404** | Not Found | Resource not found |
| **409** | Conflict | Resource already exists |
| **422** | Validation Error | Invalid data format |
| **500** | Server Error | Internal server error |

### Common Error Examples

#### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

#### 403 Forbidden
```json
{
  "detail": "Insufficient permissions"
}
```

#### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

---

## Rate Limiting

**Status:** Coming Soon

Planned rate limits:
- **Free Tier:** 1,000 requests/hour
- **Professional:** 10,000 requests/hour
- **Enterprise:** Unlimited

---

## API Endpoints

### Health Check

#### Check System Health
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "database": "connected"
}
```

---

## Authentication Endpoints

Base Path: `/api/v1/auth`

### 1. Register User

```http
POST /api/v1/auth/register
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "full_name": "John Doe",
  "role": "ECOMMERCE"
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "ECOMMERCE",
  "is_active": true,
  "created_at": "2025-12-20T10:00:00Z"
}
```

### 2. Login

```http
POST /api/v1/auth/login
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response (200):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

### 3. Refresh Token

```http
POST /api/v1/auth/refresh
```

**Headers:**
```http
Authorization: Bearer <refresh_token>
```

**Response (200):**
```json
{
  "access_token": "new_access_token",
  "refresh_token": "new_refresh_token",
  "token_type": "bearer"
}
```

### 4. Get Current User

```http
GET /api/v1/auth/me
```

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "ECOMMERCE",
  "agency_id": "uuid",
  "ecommerce_id": "uuid",
  "is_active": true,
  "created_at": "2025-12-20T10:00:00Z"
}
```

### 5. Logout

```http
POST /api/v1/auth/logout
```

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "message": "Successfully logged out"
}
```

### 6. Extend Session

```http
POST /api/v1/auth/extend-session
```

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "access_token": "new_access_token",
  "refresh_token": "new_refresh_token",
  "token_type": "bearer"
}
```

---

## User Management

Base Path: `/api/v1/users`

### 1. Create User

```http
POST /api/v1/users
```

**Permissions:** Super Admin, Agency Admin

**Request Body:**
```json
{
  "email": "newuser@example.com",
  "password": "SecurePass123!",
  "full_name": "Jane Smith",
  "role": "ECOMMERCE",
  "is_active": true
}
```

### 2. List Users

```http
GET /api/v1/users?skip=0&limit=100
```

**Query Parameters:**
- `skip` (int): Number of records to skip (default: 0)
- `limit` (int): Maximum records to return (default: 100)

### 3. Get User

```http
GET /api/v1/users/{user_id}
```

### 4. Update User

```http
PUT /api/v1/users/{user_id}
```

**Request Body:**
```json
{
  "full_name": "Jane Doe",
  "is_active": true
}
```

### 5. Delete User

```http
DELETE /api/v1/users/{user_id}
```

**Response (204):** No content

---

## Super Admin

Base Path: `/api/v1/admin`

**Permissions:** Super Admin only

### Subscription Plans

#### 1. Create Subscription Plan

```http
POST /api/v1/admin/subscription-plans
```

**Request Body:**
```json
{
  "name": "Professional",
  "description": "For growing agencies",
  "price": 99.00,
  "interval": "MONTHLY",
  "features": {
    "max_ecommerce": 10,
    "api_calls_per_month": 100000,
    "storage_gb": 50
  },
  "is_active": true
}
```

#### 2. List Subscription Plans

```http
GET /api/v1/admin/subscription-plans
```

#### 3. Get Subscription Plan

```http
GET /api/v1/admin/subscription-plans/{plan_id}
```

#### 4. Update Subscription Plan

```http
PUT /api/v1/admin/subscription-plans/{plan_id}
```

#### 5. Delete Subscription Plan

```http
DELETE /api/v1/admin/subscription-plans/{plan_id}
```

### Agencies

#### 1. Create Agency

```http
POST /api/v1/admin/agencies
```

**Request Body:**
```json
{
  "name": "Acme Digital",
  "subscription_plan_id": "plan-uuid",
  "admin_email": "admin@acme.com",
  "admin_password": "SecurePass123!",
  "admin_full_name": "John Doe",
  "max_ecommerce": 10,
  "settings": {
    "custom_domain": true,
    "white_label": true
  }
}
```

**Response (201):**
```json
{
  "agency": {
    "id": "uuid",
    "name": "Acme Digital",
    "subscription_plan_id": "plan-uuid",
    "max_ecommerce": 10,
    "is_active": true,
    "created_at": "2025-12-20T10:00:00Z"
  },
  "admin_user": {
    "id": "uuid",
    "email": "admin@acme.com",
    "full_name": "John Doe",
    "role": "AGENCY_ADMIN"
  }
}
```

#### 2. List Agencies

```http
GET /api/v1/admin/agencies
```

#### 3. Get Agency

```http
GET /api/v1/admin/agencies/{agency_id}
```

#### 4. Update Agency

```http
PUT /api/v1/admin/agencies/{agency_id}
```

#### 5. Delete Agency

```http
DELETE /api/v1/admin/agencies/{agency_id}
```

---

## Agency Admin

Base Path: `/api/v1/agencies`

**Permissions:** Agency Admin

### E-commerce Tenants

#### 1. Create E-commerce Tenant

```http
POST /api/v1/agencies/ecommerce
```

**Request Body:**
```json
{
  "name": "Fashion Store",
  "domain": "fashion.example.com",
  "admin_email": "store@fashion.com",
  "admin_password": "SecurePass123!",
  "admin_full_name": "Store Manager",
  "settings": {
    "currency": "USD",
    "timezone": "America/New_York",
    "tax_rate": 8.5,
    "shipping_enabled": true
  }
}
```

#### 2. List E-commerce Tenants

```http
GET /api/v1/agencies/ecommerce
```

#### 3. Get E-commerce Tenant

```http
GET /api/v1/agencies/ecommerce/{ecommerce_id}
```

#### 4. Update E-commerce Tenant

```http
PUT /api/v1/agencies/ecommerce/{ecommerce_id}
```

#### 5. Delete E-commerce Tenant

```http
DELETE /api/v1/agencies/ecommerce/{ecommerce_id}
```

#### 6. Get Tenant Statistics

```http
GET /api/v1/agencies/ecommerce/{ecommerce_id}/stats
```

**Response (200):**
```json
{
  "total_products": 150,
  "total_orders": 450,
  "total_customers": 320,
  "total_revenue": 45600.00,
  "active_carts": 25
}
```

#### 7. Regenerate API Key

```http
POST /api/v1/agencies/ecommerce/{ecommerce_id}/regenerate-api-key
```

**Description:** Rotate the API key for an e-commerce tenant. The old key is immediately invalidated.

**Permissions:** Agency Admin only

**Response (200):**
```json
{
  "message": "API key regenerated successfully",
  "api_key": "new_secure_32_byte_key_here",
  "ecommerce_id": "uuid",
  "warning": "Save this key securely. It will not be shown again."
}
```

**Security Features:**
- Generates cryptographically secure 32-byte URL-safe token
- Old API key immediately invalidated
- New key only displayed once
- Agency admin authorization required
- Tenant ownership validated

**Use Cases:**
- Compromised API key
- Routine security rotation
- Access revocation
- Compliance requirements

---

## Products

Base Path: `/api/v1/products`

**Permissions:** E-commerce User

### 1. Create Product

```http
POST /api/v1/products
```

**Request Body:**
```json
{
  "name": "Premium T-Shirt",
  "description": "Comfortable cotton t-shirt",
  "sku": "TSHIRT-001",
  "price": 29.99,
  "compare_at_price": 39.99,
  "cost_price": 15.00,
  "category": "Apparel",
  "tags": ["clothing", "t-shirt", "cotton"],
  "images": ["https://example.com/image1.jpg"],
  "variants": [
    {"size": "S", "color": "Blue"},
    {"size": "M", "color": "Blue"}
  ],
  "initial_quantity": 100,
  "low_stock_threshold": 10,
  "weight": 0.2,
  "weight_unit": "kg",
  "is_active": true
}
```

### 2. List Products

```http
GET /api/v1/products?skip=0&limit=100&is_active=true&category=Apparel
```

**Query Parameters:**
- `skip` (int): Pagination offset
- `limit` (int): Maximum results
- `is_active` (bool): Filter by active status
- `category` (string): Filter by category

### 3. Get Product

```http
GET /api/v1/products/{product_id}
```

### 4. Update Product

```http
PUT /api/v1/products/{product_id}
```

### 5. Delete Product

```http
DELETE /api/v1/products/{product_id}
```

### 6. Get Product Inventory

```http
GET /api/v1/products/{product_id}/inventory
```

**Response (200):**
```json
{
  "product_id": "uuid",
  "quantity": 100,
  "reserved_quantity": 5,
  "available_quantity": 95,
  "low_stock_threshold": 10,
  "is_low_stock": false
}
```

---

## Orders

Base Path: `/api/v1/orders`

**Permissions:** E-commerce User

### 1. Create Order

```http
POST /api/v1/orders
```

**Request Body:**
```json
{
  "customer_id": "customer-uuid",
  "items": [
    {
      "product_id": "product-uuid",
      "quantity": 2,
      "price": 29.99
    }
  ],
  "coupon_code": "WELCOME10",
  "shipping_cost": 5.00,
  "tax_amount": 5.40,
  "shipping_address": {
    "street": "123 Main St",
    "city": "New York",
    "state": "NY",
    "country": "USA",
    "postal_code": "10001"
  },
  "notes": "Please handle with care"
}
```

### 2. List Orders

```http
GET /api/v1/orders?skip=0&limit=100&status=PENDING
```

**Query Parameters:**
- `status` (string): PENDING, PROCESSING, SHIPPED, DELIVERED, CANCELLED
- `customer_id` (uuid): Filter by customer

### 3. Get Order

```http
GET /api/v1/orders/{order_id}
```

### 4. Update Order Status

```http
PUT /api/v1/orders/{order_id}/status
```

**Request Body:**
```json
{
  "status": "SHIPPED",
  "tracking_number": "1234567890"
}
```

### 5. Cancel Order

```http
POST /api/v1/orders/{order_id}/cancel
```

**Response (200):**
```json
{
  "message": "Order cancelled successfully",
  "order_id": "uuid",
  "status": "CANCELLED",
  "refund_amount": 64.39
}
```

---

## Customers

Base Path: `/api/v1/customers`

**Permissions:** E-commerce User

### 1. Create Customer

```http
POST /api/v1/customers
```

**Request Body:**
```json
{
  "email": "customer@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "addresses": [
    {
      "type": "shipping",
      "street": "123 Main St",
      "city": "New York",
      "state": "NY",
      "country": "USA",
      "postal_code": "10001",
      "is_default": true
    }
  ]
}
```

### 2. List Customers

```http
GET /api/v1/customers?skip=0&limit=100
```

### 3. Get Customer

```http
GET /api/v1/customers/{customer_id}
```

### 4. Update Customer

```http
PUT /api/v1/customers/{customer_id}
```

### 5. Delete Customer

```http
DELETE /api/v1/customers/{customer_id}
```

### 6. Get Customer Orders

```http
GET /api/v1/customers/{customer_id}/orders
```

---

## Shopping Cart

Base Path: `/api/v1/cart`

**Permissions:** E-commerce User

### 1. Add to Cart

```http
POST /api/v1/cart/items
```

**Request Body:**
```json
{
  "customer_id": "customer-uuid",
  "product_id": "product-uuid",
  "quantity": 2
}
```

### 2. Get Cart

```http
GET /api/v1/cart/{customer_id}
```

### 3. Update Cart Item

```http
PUT /api/v1/cart/items/{item_id}
```

**Request Body:**
```json
{
  "quantity": 3
}
```

### 4. Remove from Cart

```http
DELETE /api/v1/cart/items/{item_id}
```

### 5. Checkout

```http
POST /api/v1/cart/{customer_id}/checkout
```

**Request Body:**
```json
{
  "coupon_code": "WELCOME10",
  "shipping_address": {
    "street": "123 Main St",
    "city": "New York",
    "state": "NY",
    "country": "USA",
    "postal_code": "10001"
  }
}
```

---

## Coupons

Base Path: `/api/v1/coupons`

**Permissions:** E-commerce User

### 1. Create Coupon

```http
POST /api/v1/coupons
```

**Request Body:**
```json
{
  "code": "WELCOME10",
  "discount_type": "PERCENTAGE",
  "discount_value": 10.0,
  "min_purchase_amount": 50.0,
  "max_discount_amount": 20.0,
  "usage_limit": 100,
  "per_customer_limit": 1,
  "valid_from": "2025-12-20T00:00:00Z",
  "valid_until": "2025-12-31T23:59:59Z",
  "is_active": true
}
```

### 2. List Coupons

```http
GET /api/v1/coupons
```

### 3. Get Coupon

```http
GET /api/v1/coupons/{coupon_id}
```

### 4. Validate Coupon

```http
POST /api/v1/coupons/validate
```

**Request Body:**
```json
{
  "code": "WELCOME10",
  "cart_amount": 75.00,
  "customer_id": "customer-uuid"
}
```

### 5. Update Coupon

```http
PUT /api/v1/coupons/{coupon_id}
```

### 6. Delete Coupon

```http
DELETE /api/v1/coupons/{coupon_id}
```

---

## Webhooks

Base Path: `/api/v1/webhooks`

**Permissions:** E-commerce User

### 1. Create Webhook

```http
POST /api/v1/webhooks
```

**Request Body:**
```json
{
  "url": "https://yourapp.com/webhook",
  "events": ["order.created", "order.updated", "payment.completed"],
  "is_active": true,
  "secret": "your-webhook-secret"
}
```

### 2. List Webhooks

```http
GET /api/v1/webhooks
```

### 3. Get Webhook

```http
GET /api/v1/webhooks/{webhook_id}
```

### 4. Update Webhook

```http
PUT /api/v1/webhooks/{webhook_id}
```

### 5. Delete Webhook

```http
DELETE /api/v1/webhooks/{webhook_id}
```

### 6. Test Webhook

```http
POST /api/v1/webhooks/{webhook_id}/test
```

### 7. Get Webhook Deliveries

```http
GET /api/v1/webhooks/{webhook_id}/deliveries
```

### 8. Retry Webhook Delivery

```http
POST /api/v1/webhooks/deliveries/{delivery_id}/retry
```

### Supported Events

- `order.created`
- `order.updated`
- `order.cancelled`
- `payment.completed`
- `payment.failed`
- `product.created`
- `product.updated`
- `inventory.low_stock`
- `customer.created`

---

## Reviews

Base Path: `/api/v1/reviews`

**Permissions:** E-commerce User

### 1. Create Review

```http
POST /api/v1/reviews
```

**Request Body:**
```json
{
  "product_id": "product-uuid",
  "customer_id": "customer-uuid",
  "rating": 5,
  "title": "Excellent product!",
  "comment": "Very happy with this purchase",
  "verified_purchase": true
}
```

### 2. List Reviews

```http
GET /api/v1/reviews?product_id=uuid&approved=true
```

**Query Parameters:**
- `product_id` (uuid): Filter by product
- `customer_id` (uuid): Filter by customer
- `approved` (bool): Filter by approval status
- `min_rating` (int): Minimum rating (1-5)

### 3. Get Review

```http
GET /api/v1/reviews/{review_id}
```

### 4. Update Review

```http
PUT /api/v1/reviews/{review_id}
```

### 5. Delete Review

```http
DELETE /api/v1/reviews/{review_id}
```

### 6. Approve Review

```http
POST /api/v1/reviews/{review_id}/approve
```

### 7. Mark Review Helpful

```http
POST /api/v1/reviews/{review_id}/helpful
```

### 8. Get Product Reviews

```http
GET /api/v1/reviews/product/{product_id}
```

### 9. Get Review Statistics

```http
GET /api/v1/reviews/product/{product_id}/stats
```

**Response (200):**
```json
{
  "average_rating": 4.5,
  "total_reviews": 150,
  "rating_distribution": {
    "5": 100,
    "4": 30,
    "3": 10,
    "2": 5,
    "1": 5
  }
}
```

---

## Refunds

Base Path: `/api/v1/refunds`

**Permissions:** E-commerce User (customers can request, admins can process)

### 1. Create Refund Request

**POST** `/api/v1/refunds`

Create a new refund request for an order.

**Request Body:**
```json
{
  "order_id": "uuid",
  "amount": 99.99,
  "reason": "DEFECTIVE_PRODUCT",
  "customer_notes": "Product arrived damaged"
}
```

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "order_id": "uuid",
  "ecommerce_id": "uuid",
  "refund_number": "REF-ABC123XYZ",
  "amount": 99.99,
  "reason": "DEFECTIVE_PRODUCT",
  "status": "REQUESTED",
  "customer_notes": "Product arrived damaged",
  "admin_notes": null,
  "transaction_id": null,
  "refund_method": null,
  "inventory_returned": false,
  "requested_at": "2025-12-20T10:30:00Z",
  "approved_at": null,
  "processed_at": null,
  "completed_at": null,
  "created_at": "2025-12-20T10:30:00Z",
  "updated_at": "2025-12-20T10:30:00Z"
}
```

**Refund Reasons:**
- `CUSTOMER_REQUEST`
- `DEFECTIVE_PRODUCT`
- `WRONG_ITEM`
- `NOT_AS_DESCRIBED`
- `DAMAGED_IN_TRANSIT`
- `ORDER_CANCELLED`
- `OTHER`

---

### 2. List Refunds

**GET** `/api/v1/refunds?skip=0&limit=100&status_filter=REQUESTED`

List all refunds for the e-commerce store.

**Query Parameters:**
- `skip` - Number of records to skip (default: 0)
- `limit` - Max records to return (default: 100)
- `status_filter` - Filter by status (optional)

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "order_id": "uuid",
    "refund_number": "REF-ABC123XYZ",
    "amount": 99.99,
    "reason": "DEFECTIVE_PRODUCT",
    "status": "REQUESTED",
    "requested_at": "2025-12-20T10:30:00Z"
  }
]
```

---

### 3. Get Refund Details

**GET** `/api/v1/refunds/{refund_id}`

Get detailed information about a specific refund.

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "order_id": "uuid",
  "ecommerce_id": "uuid",
  "refund_number": "REF-ABC123XYZ",
  "amount": 99.99,
  "reason": "DEFECTIVE_PRODUCT",
  "status": "COMPLETED",
  "customer_notes": "Product arrived damaged",
  "admin_notes": "Refund approved. Item returned.",
  "transaction_id": "TXN-123456",
  "refund_method": "CREDIT_CARD",
  "inventory_returned": true,
  "requested_at": "2025-12-20T10:30:00Z",
  "approved_at": "2025-12-20T11:00:00Z",
  "processed_at": "2025-12-20T11:15:00Z",
  "completed_at": "2025-12-20T11:20:00Z"
}
```

---

### 4. Approve/Reject Refund

**POST** `/api/v1/refunds/{refund_id}/approve`

Approve or reject a refund request (Admin only).

**Request Body:**
```json
{
  "approve": true,
  "admin_notes": "Refund approved. Item returned in good condition."
}
```

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "status": "APPROVED",
  "approved_at": "2025-12-20T11:00:00Z",
  "admin_notes": "Refund approved. Item returned in good condition."
}
```

**Refund Status Flow:**
`REQUESTED` → `APPROVED` → `PROCESSING` → `COMPLETED`
or
`REQUESTED` → `REJECTED`

---

### 5. Process Refund

**POST** `/api/v1/refunds/{refund_id}/process?transaction_id=TXN-123&refund_method=CREDIT_CARD&return_inventory=true`

Process an approved refund transaction (Admin only).

**Query Parameters:**
- `transaction_id` - Payment gateway transaction ID (required)
- `refund_method` - Method used for refund (required)
- `return_inventory` - Return items to stock (default: true)

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "status": "COMPLETED",
  "transaction_id": "TXN-123",
  "refund_method": "CREDIT_CARD",
  "inventory_returned": true,
  "processed_at": "2025-12-20T11:15:00Z",
  "completed_at": "2025-12-20T11:20:00Z"
}
```

**Features:**
- Automatically returns inventory when `return_inventory=true`
- Updates order status to `REFUNDED` for full refunds
- Tracks complete transaction history

---

### 6. Update Refund

**PATCH** `/api/v1/refunds/{refund_id}`

Update refund details (Admin only).

**Request Body:**
```json
{
  "admin_notes": "Updated notes",
  "status": "PROCESSING",
  "transaction_id": "TXN-456"
}
```

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "admin_notes": "Updated notes",
  "status": "PROCESSING",
  "transaction_id": "TXN-456",
  "updated_at": "2025-12-20T11:30:00Z"
}
```

---

## Audit Logs

Base Path: `/api/v1/audit-logs`

**Permissions:** Super Admin, Agency Admin

### 1. List Audit Logs

```http
GET /api/v1/audit-logs?skip=0&limit=100
```

**Query Parameters:**
- `user_id` (uuid): Filter by user
- `action` (string): CREATE, UPDATE, DELETE, LOGIN, LOGOUT
- `resource_type` (string): user, product, order, etc.
- `start_date` (datetime): Filter from date
- `end_date` (datetime): Filter to date

### 2. Get Audit Log

```http
GET /api/v1/audit-logs/{log_id}
```

### 3. Get User Audit Logs

```http
GET /api/v1/audit-logs/user/{user_id}
```

### 4. Get Resource Audit Logs

```http
GET /api/v1/audit-logs/resource/{resource_type}/{resource_id}
```

---

## Testing with cURL

### Example: Complete Workflow

```bash
# 1. Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123!",
    "full_name": "Test User",
    "role": "ECOMMERCE"
  }'

# 2. Login
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123!"
  }' | jq -r '.access_token')

# 3. Create Product
curl -X POST http://localhost:8000/api/v1/products \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Product",
    "sku": "TEST-001",
    "price": 19.99,
    "initial_quantity": 100
  }'

# 4. List Products
curl -X GET http://localhost:8000/api/v1/products \
  -H "Authorization: Bearer $TOKEN"
```

---

## Postman Collection

Import the Postman collection for easier testing:

1. Download the collection from `/docs/postman_collection.json`
2. Import into Postman
3. Set environment variables:
   - `base_url`: http://localhost:8000
   - `access_token`: Your JWT token

---

## SDK Support

**Coming Soon:**
- Python SDK
- JavaScript/TypeScript SDK
- PHP SDK
- Ruby SDK

---

## API Versioning

Current version: **v1**

Base path: `/api/v1`

Future versions will be released under `/api/v2`, `/api/v3`, etc.

---

## Support

For API support:
- **Documentation:** [GitHub Repository](https://github.com/sumant1512/msuite-server)
- **Issues:** [GitHub Issues](https://github.com/sumant1512/msuite-server/issues)
- **Email:** sumantmishra511@gmail.com

---

**Last Updated:** December 2025
