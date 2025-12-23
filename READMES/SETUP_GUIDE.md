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

> 💡 **Note:** This guide provides instructions for both **macOS** and **Windows** operating systems.

### 1. Install Python 3.12+

#### macOS

**Check if Python 3.12+ is installed:**

```bash
python3 --version
```

**Option A: Using Homebrew (recommended):**

```bash
brew install python@3.12
```

**Option B: Using pyenv (best for version management):**

```bash
# Install pyenv
brew install pyenv

# Install Python 3.12
pyenv install 3.12.7

# Set as global version
pyenv global 3.12.7

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

#### Windows

**Option A: Using Official Installer (recommended):**

1. Download Python 3.12+ from https://www.python.org/downloads/
2. Run the installer
3. ✅ **IMPORTANT:** Check "Add Python to PATH" during installation
4. Click "Install Now"

**Option B: Using winget (Windows Package Manager):**

```powershell
winget install Python.Python.3.12
```

**Option C: Using Chocolatey:**

```powershell
choco install python --version=3.12.0
```

**Verify installation (PowerShell or Command Prompt):**

```powershell
python --version  # Should show Python 3.12.x
```

**If not found, add to PATH manually:**

1. Search "Environment Variables" in Windows
2. Edit "Path" under System Variables
3. Add: `C:\Users\YourUsername\AppData\Local\Programs\Python\Python312`
4. Add: `C:\Users\YourUsername\AppData\Local\Programs\Python\Python312\Scripts`
5. Restart terminal

### 2. Install Poetry

Poetry is the dependency manager for this project.

#### macOS

**Using official installer (recommended):**

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

**Or using Homebrew:**

```bash
brew install poetry
```

**Add to PATH (if using official installer):**

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
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

#### Windows

**Option A: Using Official Installer (PowerShell - recommended):**

```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```

**Option B: Using pip:**

```powershell
pip install poetry
```

**Option C: Using Chocolatey:**

```powershell
choco install poetry
```

**Add to PATH (if needed):**

1. Poetry is usually installed at: `%APPDATA%\Python\Scripts\poetry.exe`
2. Search "Environment Variables" in Windows
3. Edit "Path" under User Variables
4. Add: `%APPDATA%\Python\Scripts`
5. Restart PowerShell/Command Prompt

**Verify installation:**

```powershell
poetry --version
```

**Configure Poetry:**

```powershell
# Create virtualenvs in project directory
poetry config virtualenvs.in-project true
```

### 3. Install PostgreSQL (if not installed)

#### macOS

**Using Homebrew:**

```bash
brew install postgresql@14
brew services start postgresql@14

# Add to PATH (Apple Silicon)
echo 'export PATH="/opt/homebrew/opt/postgresql@14/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# Or for Intel Macs
echo 'export PATH="/usr/local/opt/postgresql@14/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

**Verify installation:**

```bash
psql --version
createdb --version
```

#### Windows

**Option A: Using Official Installer (recommended):**

1. Download PostgreSQL 14+ from https://www.postgresql.org/download/windows/
2. Run the installer (postgresql-14.x-windows-x64.exe)
3. During installation:
   - Set password for `postgres` user (remember this!)
   - Default port: 5432
   - Select components: PostgreSQL Server, pgAdmin 4, Command Line Tools
4. Complete installation

**Option B: Using Chocolatey:**

```powershell
choco install postgresql14 --params '/Password:YourPassword'
```

**Add to PATH (if needed):**

1. Default installation path: `C:\Program Files\PostgreSQL\14\bin`
2. Search "Environment Variables"
3. Edit "Path" under System Variables
4. Add: `C:\Program Files\PostgreSQL\14\bin`
5. Restart terminal

**Verify installation (Command Prompt or PowerShell):**

```powershell
psql --version
createdb --version
```

**Start PostgreSQL service (if not running):**

```powershell
# PowerShell (Run as Administrator)
Start-Service postgresql-x64-14

# Or use Windows Services
# Search "Services" → Find "postgresql-x64-14" → Right-click → Start
```

### 4. Create Database

#### macOS

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

#### Windows

**Option A: Using psql (PowerShell or Command Prompt):**

```powershell
# Connect as postgres user
psql -U postgres
# Enter password when prompted

# In psql:
CREATE DATABASE "MSuite";
\q
```

**Option B: Using createdb:**

```powershell
# Command Prompt or PowerShell
createdb -U postgres MSuite
# Enter password when prompted
```

**If authentication fails:**

```powershell
# Option 1: Set PGPASSWORD temporarily (PowerShell)
$env:PGPASSWORD = "your_postgres_password"
createdb -U postgres MSuite

# Option 2: Set PGPASSWORD temporarily (Command Prompt)
set PGPASSWORD=your_postgres_password
createdb -U postgres MSuite

# Option 3: Use connection string
psql "postgresql://postgres:your_password@localhost:5432/postgres" -c "CREATE DATABASE \"MSuite\";"
```

**Option C: Using SQL client (TablePlus, DBeaver, pgAdmin 4, etc.):**

- Connect to PostgreSQL server
- Create new database named "MSuite"

## Project Setup

### 1. Setup Virtual Environment

Poetry is configured to create virtual environments in the project directory.

**Check Poetry configuration:**

_macOS/Linux:_

```bash
poetry config --list | grep virtualenvs
```

_Windows (PowerShell):_

```powershell
poetry config --list | Select-String virtualenvs
```

_Windows (Command Prompt):_

```cmd
poetry config --list | findstr virtualenvs
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

_macOS/Linux:_

```bash
source .venv/bin/activate
```

_Windows (PowerShell):_

```powershell
.\.venv\Scripts\Activate.ps1

# If you get execution policy error, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

_Windows (Command Prompt):_

```cmd
.venv\Scripts\activate.bat
```

**Or use Poetry commands directly (recommended for cross-platform):**

```bash
poetry run python --version
poetry run uvicorn app.main:app --reload
```

### 2. Configure Environment

Copy the example environment file and update with your settings:

_macOS/Linux:_

```bash
cp .env.example .env
```

_Windows (PowerShell):_

```powershell
Copy-Item .env.example .env
```

_Windows (Command Prompt):_

```cmd
copy .env.example .env
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

_macOS/Linux:_

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
# Or use Poetry:
poetry run python -c "import secrets; print(secrets.token_urlsafe(32))"
```

_Windows (PowerShell):_

```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
# Or use Poetry:
poetry run python -c "import secrets; print(secrets.token_urlsafe(32))"
```

_Windows (Command Prompt):_

```cmd
python -c "import secrets; print(secrets.token_urlsafe(32))"
rem Or use Poetry:
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

_macOS/Linux:_

```bash
curl http://localhost:8000/
```

_Windows (PowerShell):_

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/" -Method Get
# Or using curl (if available)
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

_macOS/Linux:_

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

_Windows (PowerShell):_

```powershell
$body = @{
    email = "admin@example.com"
    password = "SecurePass123!"
    full_name = "Admin User"
    role = "SUPER_ADMIN"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/register" `
  -Method Post `
  -ContentType "application/json" `
  -Body $body
```

### 4. Login

_macOS/Linux:_

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "SecurePass123!"
  }'
```

_Windows (PowerShell):_

```powershell
$body = @{
    email = "admin@example.com"
    password = "SecurePass123!"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" `
  -Method Post `
  -ContentType "application/json" `
  -Body $body
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

**Solution (macOS/Linux):**

```bash
# Create the database
createdb -U postgres MSuite

# Or using psql
psql -U postgres -c "CREATE DATABASE \"MSuite\";"
```

**Solution (Windows):**

```powershell
# PowerShell or Command Prompt
createdb -U postgres MSuite

# Or using psql
psql -U postgres -c "CREATE DATABASE \"MSuite\";"

# If password prompt doesn't work, set PGPASSWORD first:
$env:PGPASSWORD = "your_password"
createdb -U postgres MSuite
```

### Issue: "password authentication failed for user postgres"

**Solution:**
Update your `.env` file with correct PostgreSQL credentials:

```env
DATABASE_URL=postgresql://postgres:YOUR_ACTUAL_PASSWORD@localhost:5432/MSuite
```

**Windows-specific:**

- Check PostgreSQL password set during installation
- Try connecting with pgAdmin 4 to verify credentials
- Check if PostgreSQL service is running:
  ```powershell
  Get-Service postgresql-x64-14
  ```

### Issue: "command not found: psql" or "'psql' is not recognized"

**Solution (macOS):**

```bash
# Install PostgreSQL
brew install postgresql@14

# Add to PATH
echo 'export PATH="/opt/homebrew/opt/postgresql@14/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

**Solution (Windows):**

```powershell
# Add PostgreSQL to PATH
# 1. Search "Environment Variables" in Windows
# 2. Edit "Path" under System Variables
# 3. Add: C:\Program Files\PostgreSQL\14\bin
# 4. Restart terminal

# Or temporarily add to current session:
$env:PATH += ";C:\Program Files\PostgreSQL\14\bin"

# Verify:
psql --version
```

### Issue: "Port 8000 is already in use"

**Solution (macOS/Linux):**

```bash
# Find process using port 8000
lsof -ti:8000

# Kill the process
lsof -ti:8000 | xargs kill -9
```

**Solution (Windows):**

```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Note the PID (last column), then kill it:
taskkill /PID <PID> /F

# Or use PowerShell:
Get-NetTCPConnection -LocalPort 8000 | Select-Object -ExpandProperty OwningProcess | ForEach-Object { Stop-Process -Id $_ -Force }
```

### Issue: PowerShell Execution Policy Error

**Solution (Windows):**

```powershell
# When activating venv or running scripts
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Or bypass for current session only:
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
```

### Issue: "ImportError: cannot import name..."

**Solution:**

```bash
# Reinstall dependencies
poetry install --no-root
```

### Issue: "Unable to connect to database" or connection timeouts

**Solution:**

_Check PostgreSQL service is running (macOS):_

```bash
brew services list | grep postgresql
# If not running:
brew services start postgresql@14
```

_Check PostgreSQL service is running (Windows):_

```powershell
# Check service status
Get-Service postgresql-x64-14

# If not running, start it:
Start-Service postgresql-x64-14

# Or use Services GUI:
# Search "Services" → Find "postgresql-x64-14" → Start
```

_Verify database exists:_

```bash
# macOS/Linux:
psql -U postgres -l | grep MSuite

# Windows (PowerShell):
psql -U postgres -l | Select-String MSuite
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
