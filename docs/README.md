# MSuite Documentation Index

Central hub for all project documentation.

---

## Quick Links
- Architecture: ../ARCHITECTURE.md
- Setup Guide: ../SETUP_GUIDE.md
- API Documentation: ../API_DOCUMENTATION.md
- Routes Summary: ../ROUTES_SUMMARY.md
- Features: ../FEATURES.md
- Security: ../SECURITY.md
- Deployment: ../DEPLOYMENT.md
- Testing: ../TESTING.md
- Contributing: ../CONTRIBUTING.md
- Session Management: ../SESSION_MANAGEMENT_IMPLEMENTATION.md
- Project Structure: ../PROJECT_STRUCTURE.md

---

## Usage
- Start at API docs for endpoints.
- Use Postman collection below for quick testing.

Postman Collection: postman_collection.json

### Postman Environments

- Local: postman_env_local.json
- Staging: postman_env_staging.json
- Production: postman_env_prod.json

### Auto-Token Setup

- After running "Auth: Login", the collection test script auto-saves `access_token` and `refresh_token` into the selected environment.
- Subsequent requests use `Authorization: Bearer {{access_token}}` automatically.

### How to Use

1. Import `postman_collection.json` and choose an environment (local/staging/prod).
2. Run "Auth: Register" (optional) then "Auth: Login".
3. Confirm the environment now has `access_token`.
4. Call any protected endpoints.

---

Last Updated: December 2025
