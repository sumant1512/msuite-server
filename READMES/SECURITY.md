# Security Guide

Best practices and security configurations for MSuite.

---

## 📑 Table of Contents
- [Overview](#overview)
- [Authentication](#authentication)
- [Authorization](#authorization)
- [Session Management](#session-management)
- [Password Security](#password-security)
- [Transport Security](#transport-security)
- [Data Protection](#data-protection)
- [CORS Configuration](#cors-configuration)
- [Logging & Audit](#logging--audit)
- [Rate Limiting](#rate-limiting)
- [Dependency Security](#dependency-security)
- [Operational Security](#operational-security)
- [Incident Response](#incident-response)

---

## Overview

MSuite is designed with a security-first approach, including strict authentication, authorization, session controls, and audit logging.

---

## Authentication
- Use JWTs for access and refresh tokens
- Access token expiry: 60 minutes
- Refresh token expiry: 7 days
- Tokens stored client-side; never store refresh tokens in localStorage
- Rotate tokens frequently using `extend-session`

---

## Authorization
- Role-based access control (RBAC) with three roles:
  - `SUPER_ADMIN`: system-wide privileges
  - `AGENCY_ADMIN`: agency-scoped privileges
  - `ECOMMERCE`: tenant-scoped privileges
- Enforce tenant isolation via `agency_id` and `ecommerce_id` filters

---

## Session Management
- Inactivity timeout: 30 minutes
- Extend session using `/api/v1/auth/extend-session`
- Logout blacklists tokens immediately
- Track user activity on every authenticated request

---

## Password Security
- Hash passwords using bcrypt via `passlib`
- Minimum password length: 12 characters (recommend)
- Enforce complexity (uppercase, lowercase, digit, symbol)
- Never log or store plaintext passwords

---

## Transport Security
- Always use HTTPS in production
- Redirect HTTP to HTTPS at the load balancer
- Set `Secure`, `HttpOnly`, `SameSite` attributes for cookies (if used)

---

## Data Protection
- Restrict data access by tenant boundaries
- Validate all inputs via Pydantic
- Avoid storing sensitive data unless necessary
- Sanitize user-generated content

---

## CORS Configuration
- Restrict origins using `BACKEND_CORS_ORIGINS` in `.env`
- Allow only necessary headers and methods
- Disable CORS in production unless required

---

## Logging & Audit
- Log all critical events (login, logout, create/update/delete)
- Capture IP address and user-agent
- Store audit logs per tenant and globally
- Monitor for abnormal patterns

---

## Rate Limiting
- Planned per-tenant rate limiting to prevent abuse
- Suggested limits:
  - Free: 1,000 req/hour
  - Pro: 10,000 req/hour
  - Enterprise: Custom

---

## Dependency Security
- Pin versions in `pyproject.toml`
- Run `poetry update` cautiously
- Use `pip-audit` or `poetry audit` (if available)

---

## Operational Security
- Rotate secrets periodically
- Store secrets in environment variables or a secrets manager
- Backup databases regularly
- Restrict database access to internal network

---

## Incident Response
- Enable error tracking (Sentry, etc.)
- Define on-call procedures
- Document response steps for security incidents

---

**Last Updated:** December 2025
