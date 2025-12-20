# Deployment Guide

Production deployment instructions for MSuite.

---

## 📑 Table of Contents
- [Overview](#overview)
- [Environment Requirements](#environment-requirements)
- [Configuration](#configuration)
- [Database](#database)
- [Application Server](#application-server)
- [Reverse Proxy](#reverse-proxy)
- [Static Assets](#static-assets)
- [Monitoring](#monitoring)
- [Backups](#backups)
- [Scaling](#scaling)
- [Zero-Downtime Deploys](#zero-downtime-deploys)

---

## Overview

This guide describes how to deploy MSuite to a production environment using Uvicorn/Gunicorn behind Nginx, with PostgreSQL as the database.

---

## Environment Requirements
- Python 3.12+
- PostgreSQL 14+
- Linux (Ubuntu 22.04 recommended)
- Nginx (or any reverse proxy)

---

## Configuration

Set environment variables via `.env` or your secrets manager:

```env
DATABASE_URL=postgresql://<user>:<pass>@<host>:5432/MSuite
SECRET_KEY=<strong-secret>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7
BACKEND_CORS_ORIGINS=["https://your-frontend.com"]
```

---

## Database
- Create database and run migrations:

```bash
poetry run alembic upgrade head
```

- Enable automated backups (daily full, hourly WAL)
- Use connection pooling (PgBouncer recommended)

---

## Application Server

Use Gunicorn with Uvicorn workers:

```bash
gunicorn app.main:app \
  -k uvicorn.workers.UvicornWorker \
  --workers 4 \
  --bind 0.0.0.0:8000 \
  --timeout 120
```

Systemd unit example (`/etc/systemd/system/msuite.service`):

```
[Unit]
Description=MSuite API Service
After=network.target

[Service]
User=www-data
WorkingDirectory=/opt/msuite-server
Environment="DATABASE_URL=postgresql://..."
Environment="SECRET_KEY=..."
ExecStart=/opt/msuite-server/.venv/bin/gunicorn app.main:app -k uvicorn.workers.UvicornWorker --workers 4 --bind 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## Reverse Proxy

Nginx config snippet:

```
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable HTTPS with Let’s Encrypt (Certbot).

---

## Static Assets
- Serve any static content (if needed) via Nginx
- Configure caching headers

---

## Monitoring
- Use metrics and logs (Prometheus/Grafana or similar)
- Error tracking (Sentry)
- Health checks (`/` and `/health`)

---

## Backups
- Daily database backups
- Test restores periodically
- Keep offsite backups

---

## Scaling
- Vertical: increase CPU/RAM, worker count
- Horizontal: add instances behind load balancer
- Database: scale read replicas, optimize indexes

---

## Zero-Downtime Deploys
- Use blue/green or rolling deployments
- Run migrations before switching traffic

---

**Last Updated:** December 2025
