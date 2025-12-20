# MSuite Server - Setup Guide

## 📑 Table of Contents

- [Prerequisites Installation](#prerequisites-installation)
  - [1. Install Python 3.12+](#1-install-python-312)
  - [2. Install Poetry](#2-install-poetry)
  - [3. Install PostgreSQL](#3-install-postgresql-if-not-installed)
  - [4. Create Database](#4-create-database)
- [Project Setup](#project-setup)
  - [1. Setup Virtual Environment](#1-setup-virtual-environment)
  - [2. Configure Environment](#2-configure-environment)
  - [3. Run Database Migrations](#3-run-database-migrations)
  - [4. Seed Database (Optional)](#4-seed-database-optional---create-initial-super-admin)
  - [5. Start the Server](#5-start-the-server)
- [Testing the API](#testing-the-api)
- [Troubleshooting](#troubleshooting)
- [Next Steps](#next-steps)
- [Development Workflow](#development-workflow)
- [Additional Resources](#additional-resources)

---

## Prerequisites Installation

### 1. Install Python 3.12+

**Check if Python 3.12+ is installed:**
```bash
python3 --version
```

**Using Homebrew (macOS):**
```bash
brew install python@3.12
```

**Using pyenv (recommended for version management):**
```bash
# Install pyenv
brew install pyenv

# Install Python 3.12
pyenv install 3.12.12

# Set as global version
pyenv global 3.12.12

# Add to shell profile (~/.zshrc or ~/.bash_profile)
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init -)"' >> ~/.zshrc
source ~/.zshrc
```

**Verify installation:**
```bash
python3 --version  # Should show Python 3.12.x
```

### 2. Install Poetry

Poetry is the dependency manager for this project.

**Using official installer (recommended):**
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

**Or using Homebrew:**
```bash
brew install poetry
```

**Verify installation:**
```bash
poetry --version
```

**Configure Poetry (optional but recommended):**
```bash
# Create virtualenvs in project directory
poetry config virtualenvs.in-project true
```

### 3. Install PostgreSQL (if not installed)

**Using Homebrew (macOS):**
```bash
brew install postgresql@14
brew services start postgresql@14

# Add to PATH (Apple Silicon)
echo 'export PATH="/opt/homebrew/opt/postgresql@14/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

**Verify installation:**
```bash
psql --version
createdb --version
```

### 4. Create Database

**Option A: Using psql command:**
```bash
psql -U postgres
CREATE DATABASE "MSuite";
\q
```

**Option B: Using createdb:**
```bash
createdb -U postgres MSuite
```

**Option C: Using SQL client (TablePlus, DBeaver, etc.):**
- Connect to PostgreSQL server
- Create new database named "MSuite"

## Project Setup

### 1. Setup Virtual Environment

Poetry is configured to create virtual environments in the project directory.

**Check Poetry configuration:**
```bash
poetry config --list | grep virtualenvs
```

**Install dependencies and create venv:**
```bash
poetry install
```

This will:
- Create a `.venv` directory in your project root
- Install all project dependencies
- Use Python 3.12+

**Verify environment setup:**
```bash
poetry env info
```

Expected output:
```
Virtualenv
Python:         3.12.x
Implementation: CPython
Path:           /path/to/project/.venv
Valid:          True
```

**Activate the environment (optional):**
```bash
source .venv/bin/activate
```

**Or use Poetry commands directly (recommended):**
```bash
poetry run python --version
poetry run uvicorn app.main:app --reload
```

### 2. Configure Environment

Copy the example environment file and update with your settings:
```bash
cp .env.example .env
```

Edit `.env` file:
```env
# Update with your PostgreSQL credentials
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/MSuite

# Generate a strong secret key (minimum 32 characters)
SECRET_KEY=your-generated-secret-key-here-min-32-chars

# Other settings (can keep defaults)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7
```

**Generate a secure SECRET_KEY:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
# Or use Poetry:
poetry run python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. Run Database Migrations

```bash
# Apply all migrations to create database tables
poetry run alembic upgrade head
```

Expected output:
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> xxxxx, Initial migration: all models
```

### 4. Seed Database (Optional - Create Initial Super Admin)

Run the seed script to create an initial Super Admin user:

```bash
poetry run python scripts/seed_db.py
```

Expected output:
```
🌱 Starting database seed...

============================================================
🎉 Database seeded successfully!
============================================================

📧 Super Admin Created:
   Email:    admin@msuite.com
   Password: Admin@123
   Name:     Super Admin
   Role:     SUPER_ADMIN
   ID:       <uuid>

⚠️  IMPORTANT: Change the password after first login!
============================================================
```

**Default Credentials:**
- **Email:** `admin@msuite.com`
- **Password:** `Admin@123`

⚠️ **Security Note:** Change this password immediately after first login in production!

### 5. Start the Server

```bash
poetry run uvicorn app.main:app --reload --port 8000
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
✅ Database connection successful
🚀 MSuite - E-Commerce BaaS started successfully
INFO:     Application startup complete.
```

## Testing the API

### 1. Access API Documentation

Open your browser:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 2. Test Health Endpoint

```bash
curl http://localhost:8000/
```

Expected response:
```json
{
  "status": "online",
  "service": "MSuite - E-Commerce BaaS",
  "version": "1.0.0"
}
```

### 3. Register a User

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "SecurePass123!",
    "full_name": "Admin User",
    "role": "SUPER_ADMIN"
  }'
```

### 4. Login

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "SecurePass123!"
  }'
```

Expected response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "uuid-here",
    "email": "admin@example.com",
    "full_name": "Admin User",
    "role": "SUPER_ADMIN",
    "is_active": true,
    "created_at": "2025-12-17T..."
  }
}
```

### 5. Test Protected Endpoint

```bash
# Replace <ACCESS_TOKEN> with the token from login response
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

## Troubleshooting

### Issue: "database MSuite does not exist"

**Solution:**
```bash
# Create the database
createdb -U postgres MSuite

# Or using psql
psql -U postgres -c "CREATE DATABASE \"MSuite\";"
```

### Issue: "password authentication failed for user postgres"

**Solution:**
Update your `.env` file with correct PostgreSQL credentials:
```env
DATABASE_URL=postgresql://postgres:YOUR_ACTUAL_PASSWORD@localhost:5432/MSuite
```

### Issue: "command not found: psql"

**Solution (macOS):**
```bash
# Install PostgreSQL
brew install postgresql@14

# Add to PATH
echo 'export PATH="/opt/homebrew/opt/postgresql@14/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### Issue: "ImportError: cannot import name..."

**Solution:**
```bash
# Reinstall dependencies
poetry install --no-root
```

### Issue: "Port 8000 already in use"

**Solution 1: Kill the process using the port (recommended)**
```bash
# Kill any process using port 8000
lsof -ti:8000 | xargs kill -9
```

**Solution 2: Use a different port**
```bash
# Use a different port
poetry run uvicorn app.main:app --reload --port 8001
```

## Next Steps

1. ✅ Create your first Super Admin user
2. 🔄 Create subscription plans (coming soon)
3. 🔄 Create agencies (coming soon)
4. 🔄 Create e-commerce tenants (coming soon)
5. 🔄 Start managing products and orders (coming soon)

## Development Workflow

### Create a new migration
```bash
poetry run alembic revision --autogenerate -m "Description"
```

### Apply migrations
```bash
poetry run alembic upgrade head
```

### Rollback migration
```bash
poetry run alembic downgrade -1
```

### Check current migration version
```bash
poetry run alembic current
```

### View migration history
```bash
poetry run alembic history
```

## Additional Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **SQLAlchemy Documentation**: https://docs.sqlalchemy.org/
- **Alembic Documentation**: https://alembic.sqlalchemy.org/
- **Pydantic Documentation**: https://docs.pydantic.dev/

## Support

For issues or questions:
- Email: sumantmishra511@gmail.com
- GitHub: https://github.com/sumant1512/msuite-server

---

**Happy Coding! 🚀**
