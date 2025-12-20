# Features Overview

Detailed features for MSuite — a hierarchical multi-tenant e-commerce Backend‑as‑a‑Service. This document centralizes feature details to avoid duplication across other docs.

---

## 📑 Table of Contents
- [Platform Overview](#platform-overview)
- [Security & Access](#security--access)
- [Role-Specific Features](#role-specific-features)
	- [Super Admin](#super-admin)
	- [Agency Admin](#agency-admin)
	- [E‑commerce User](#e-commerce-user)
- [Domain Capabilities](#domain-capabilities)
	- [Products](#products)
	- [Inventory](#inventory)
	- [Orders](#orders)
	- [Refunds & Returns](#refunds--returns)
	- [Billing & Invoicing](#billing--invoicing)
	- [Customers](#customers)
	- [Shopping Cart](#shopping-cart)
	- [Coupons](#coupons)
	- [Reviews](#reviews)
	- [Webhooks](#webhooks)
	- [Audit Logging](#audit-logging)
- [Operational Features](#operational-features)
- [Internationalization](#internationalization)
- [Future Enhancements](#future-enhancements)

---

## Platform Overview

- Multi-tenant hierarchy: Super Admin → Agency → Store (E‑commerce)
- Shared PostgreSQL database with row-level isolation via `agency_id`, `ecommerce_id`
- Modern FastAPI stack with async SQLAlchemy, Alembic migrations, Pydantic v2
- Complete REST API with OpenAPI/Swagger and ReDoc

---

## Security & Access

- **Authentication**: 
	- JWT access + refresh tokens
	- **API key authentication** for e-commerce frontend stores
	- **Subscription validation** on API key usage
- **Authorization**: Role-Based Access Control (RBAC)
	- **Self-registration restrictions** - Only customers can self-register
	- Admins must be created by authorized parent roles
- **Session Management**:
	- 30‑minute inactivity timeout
	- Session extension endpoint
	- Token blacklisting on logout/timeouts
- **Tenant Isolation**:
	- **Cross-tenant access protection** - UUID guessing prevention
	- **Automatic tenant filtering** via dependency injection
	- **validate_tenant_access()** helper for resource validation
- **Subscription Enforcement**:
	- Active subscription required for store creation
	- Expiration date validation
	- Status checks (ACTIVE/TRIAL only)
- **Security Operations**:
	- **API key rotation** for compromised keys
	- Bcrypt password hashing (via passlib)
	- HTTPS in production, strict CORS configuration

For implementation details, see `SESSION_MANAGEMENT_IMPLEMENTATION.md` and `IMPLEMENTATION_SUMMARY.md`.

---

## Role-Specific Features

### Super Admin
- Subscription Plans
	- Create, update, list, delete plans
	- Billing intervals, feature quotas (e.g., max stores, API rate limits planned)
- Agencies
	- Provision agencies linked to subscription plans
	- Enforce quotas and activation status
	- View global analytics across agencies (counts, growth, activity)
- Global Users
	- Create agency admins or system operators
	- Disable/reactivate accounts
- Governance & Compliance
	- Access global audit logs
	- Policy configuration (password rules, token expiries)
- Platform Configuration
	- System settings (CORS, security toggles)
	- Observability hooks (health checks)

### Agency Admin
- Tenant (Store) Management
	- Create, configure, update, delete e‑commerce tenants
	- Store settings: currency, timezone, tax rate, domain
	- Per‑tenant API keys and usage monitoring
	- **Secure API key rotation** - Regenerate keys for security compliance
	- **Custom resale pricing** - Set per-store pricing for white-label business models
- Agency Users
	- Invite/manage agency staff and store managers
	- Assign roles and restrict to specific tenants
- **Billing & Revenue Management**
	- **Invoice tracking** - View and manage subscription invoices
	- **Payment history** - Track payments with transaction IDs
	- **Revenue analytics** - Monitor income from all stores
- Analytics & Quotas
	- View tenant counts, product/order/customer volume, revenue snapshots
	- Enforce plan quotas (max stores, features)
- Operational Controls
	- Manage integrations at agency level (planned)
	- Export summaries and audit reports

### E‑commerce User
- Catalog & Inventory
	- Create and manage products, variants, images, categories/tags
	- Inventory tracking, low‑stock alerts, reserved quantities during ordering
- Orders & Fulfillment
	- Full lifecycle: PENDING → PROCESSING → SHIPPED → DELIVERED → CANCELLED → **REFUNDED**
	- Update statuses, add tracking numbers, handle cancellations with stock return
	- **Refund management** - Request, approve, and process refunds with workflow tracking
	- **Automatic inventory return** - Stock adjustments on refund completion
- Customers
	- Profiles with validated email/phone
	- Multiple addresses (shipping/billing)
	- Order history and spending statistics
- Shopping Cart
	- Add/update/remove items, price recomputation
	- Checkout validation (stock, coupons)
- Discounts & Engagement
	- Coupons (percentage/fixed/free shipping), limits and validity windows
	- Product reviews with moderation, verified purchase flag, helpful votes
- Integrations
	- Webhooks for events (orders, payments, products, inventory, customers)
	- HMAC signatures, retry with backoff, delivery history
- Compliance
	- Tenant‑scoped audit logs for product/order/customer changes

---

## Domain Capabilities

### Products
- Rich product model: name, description, pricing (price, compare_at_price, cost_price)
- Variants (JSON) with attributes (size/color, etc.)
- Images (list of URLs), categories, tags
- SKU validation and uniqueness per tenant

### Inventory
- Quantities: total, reserved, available
- Low‑stock threshold and flags
- Automatic reservation during order creation; release on cancellation

### Orders
- Items with price/quantity; shipping and tax amounts
- Status transitions with validation
- Cancellation flow with inventory adjustments
- Optional tracking number and notes
- **Refund relationship** - Linked to refund requests

### Refunds & Returns
- **Refund request creation** - Customers can request refunds for orders
- **Approval workflow** - Admin approval/rejection with notes
- **Processing pipeline** - REQUESTED → APPROVED → PROCESSING → COMPLETED
- **Refund reasons** - Defective, wrong item, not as described, damaged, etc.
- **Transaction tracking** - Payment gateway transaction IDs
- **Inventory management** - Automatic stock return on refund completion
- **Partial refunds** - Support for amounts less than order total
- **Status tracking** - Complete audit trail of refund lifecycle
- **Admin controls** - Process refunds, add notes, track completion

### Billing & Invoicing
- **Invoice generation** - Automated billing for subscription plans
- **Payment tracking** - Record payments with transaction details
- **Multiple payment methods** - Credit card, UPI, wallet, bank transfer, etc.
- **Invoice status** - DRAFT, SENT, PAID, OVERDUE, CANCELLED
- **Payment status** - PENDING, COMPLETED, FAILED, REFUNDED
- **Billing periods** - Monthly, quarterly, annual tracking
- **Tax calculation** - Support for tax amounts on invoices
- **Agency relationship** - Invoices linked to agencies for complete billing history
- **Gateway integration** - Store gateway responses for reconciliation

### Customers
- Core profile: first/last name, email, phone
- Address book supporting multiple entries with defaults
- Derived metrics: total orders, total spend (service‑level)

### Shopping Cart
- Customer‑scoped cart storage
- Item management with quantity updates
- Derived totals: subtotal, tax, shipping, discounts, grand total
- Expiration handling

### Coupons
- Types: PERCENTAGE, FIXED_AMOUNT, FREE_SHIPPING
- Rules: min purchase, max discount, per‑customer limits, global usage limits
- Validity: start/end timestamps, active toggle
- Validation endpoint to preview discount application

### Reviews
- 1–5 star ratings, title/comment
- Verified purchase badge (when linked to orders)
- Moderation: approve/reject; helpful votes
- Stats: average rating, distribution

### Webhooks
- Subscriptions per tenant with selected event list
- Secure delivery via HMAC signatures
- Retry policy with exponential backoff
- Delivery logs and manual retry endpoint

### Audit Logging
- Log actor, action, resource, timestamps, IP, user agent
- Filter by tenant, user, action, resource type
- Useful for compliance and forensics

---

## Operational Features
- Health checks: root and `/health`
- Alembic migrations and version history
- Environment‑driven configuration via Pydantic Settings
- Observability hooks (planned: metrics, tracing)

---

## Internationalization
- Per‑tenant currency, timezone, tax rate configuration
- Locale‑aware timestamps and monetary values (client responsibility)

---

## Future Enhancements
- Analytics dashboards and reporting
- Payment gateways (Stripe, PayPal)
- Email notifications and templates
- Advanced search and filtering
- Per‑tenant API rate limiting and quotas

---

Last Updated: December 2025
