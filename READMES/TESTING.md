# Testing Guide

Testing strategies and examples for MSuite.

---

## 📑 Table of Contents
- [Overview](#overview)
- [Test Types](#test-types)
- [Setup](#setup)
- [Running Tests](#running-tests)
- [Fixtures](#fixtures)
- [API Tests](#api-tests)
- [Database Tests](#database-tests)
- [Mocking & Stubs](#mocking--stubs)
- [Coverage](#coverage)
- [CI Integration](#ci-integration)

---

## Overview

MSuite uses `pytest` for testing with a focus on API routes, services, and database interactions.

---

## Test Types
- Unit tests (services, utils)
- Integration tests (API endpoints)
- Database tests (models, migrations)
- Security tests (auth flows)

---

## Setup

Install testing dependencies (if not already included):

```bash
poetry add --group dev pytest pytest-cov httpx
```

---

## Running Tests

```bash
poetry run pytest
poetry run pytest --cov=app --cov-report=term-missing
```

---

## Fixtures

Common fixtures:
- Test database (temporary)
- HTTP client (`httpx.AsyncClient`)
- Seed data (users, products)

---

## API Tests

Sample `tests/test_auth.py`:

```python
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.anyio
async def test_register_login_flow():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Register
        resp = await ac.post("/api/v1/auth/register", json={
            "email": "test@example.com",
            "password": "Test123!",
            "full_name": "Test User",
            "role": "ECOMMERCE"
        })
        assert resp.status_code == 201

        # Login
        resp = await ac.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "Test123!"
        })
        assert resp.status_code == 200
        token = resp.json()["access_token"]

        # Me
        resp = await ac.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
```

---

## Database Tests

- Use a separate test database
- Run migrations before tests
- Wrap tests in transactions and roll back

---

## Mocking & Stubs

- Mock external APIs (webhooks)
- Stub email/payment gateways (planned)

---

## Coverage

Target coverage: 80%+

```bash
poetry run pytest --cov=app --cov-report=html
open htmlcov/index.html
```

---

## CI Integration

- Use GitHub Actions to run tests on push/PR
- Cache Poetry and venv for speed
- Upload coverage reports

---

**Last Updated:** December 2025
