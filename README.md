# Welcome to GitHub Desktop!
# Document Management API (FastAPI)

This is your README. READMEs are where you can communicate what your project is and how to use it.
Production-oriented FastAPI project with authentication, RBAC, secure document workflow, and scalable architecture.
Bhargavi
Write your name on line 6, save it, and then head back to GitHub Desktop.
## Features

- JWT authentication with access + refresh tokens
- Password hashing using bcrypt
- Role-based access control (admin, user)
- Secure upload for PDF/JPEG/PNG documents with type and size validation
- Admin approval/rejection workflow with status history audit trail
- Soft delete (`is_deleted`, `deleted_at`)
- Secure authenticated download endpoint (no public static file exposure)
- Redis-backed caching (with in-memory fallback)
- Rate limiting on login attempts (per IP)
- API versioning under `/api/v1`
- Structured logging + request logging middleware
- Health check endpoint with DB status and uptime
- Alembic migration setup
- Basic pytest coverage

## Project Structure

```text
app/
 ├── main.py
 ├── core/
 ├── models/
 ├── schemas/
 ├── routes/
 ├── services/
 ├── dependencies/
 ├── middleware/
 └── utils/
alembic/
tests/
```

## Setup

1. Create environment file:

```bash
cp .env.example .env
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run migrations (optional, app also creates tables on startup):

```bash
alembic upgrade head
```

4. Start server:

```bash
uvicorn app.main:app --reload
```

## Core Endpoints

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/documents/upload`
- `GET /api/v1/documents/me`
- `GET /api/v1/documents` (admin filters/pagination/search)
- `PATCH /api/v1/documents/{id}/status` (admin approve/reject)
- `DELETE /api/v1/documents/{id}` (soft delete)
- `GET /api/v1/documents/{id}/download` (secure download)
- `GET /api/v1/documents/admin/stats`
- `GET /api/v1/health`

## Notes

- First registered user is assigned `admin`, all others default to `user`.
- Caches are invalidated when document state changes.