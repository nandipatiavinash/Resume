# Resume Intelligence Platform

The **Resume Intelligence Platform** is a complete, production-ready full-stack application that optimizes candidate resume data for target job descriptions using server-side LaTeX compilation, Celery workers, and multi-provider LLM adapters.

---

## Architecture

```
                                          +---------------------------------+
                                          |        Next.js Frontend         |
                                          |          (Vercel App)           |
                                          +----------------+----------------+
                                                           |
                                                           | HTTP Requests
                                                           v
                                          +----------------+----------------+
                                          |         FastAPI Backend         |
                                          |       (Railway API Node)        |
                                          +-----+----------+----------+-----+
                                                |          |          |
      +-----------------------------------------+          |          +-----------------------------------------+
      |                                                    |                                                    |
      v                                                    v                                                    v
+-----+-----+                                        +-----+-----+                                        +-----+-----+
| PostgreSQL|                                        |   Redis   |                                        |  Celery   |
| (Database)|                                        | (Broker)  |                                        | (Worker)  |
+-----------+                                        +-----+-----+                                        +-----+-----+
                                                           |                                                    |
                                                           +----------------------------------------------------+
                                                                                                                |
                                                                                                                v
                                                                                                          +-----+-----+
                                                                                                          |  XeLaTeX  |
                                                                                                          | (Subproc) |
                                                                                                          +-----+-----+
```

---

## Local Setup (5 Commands to Running)

Start postgres, redis, backend, and frontend immediately:

```bash
# 1. Clone the project and navigate to the directory
cd resume

# 2. Start PostgreSQL and Redis containers
docker-compose up -d postgres redis

# 3. Setup backend environment and install dependencies
cd backend && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt

# 4. Start local FastAPI dev server and Celery background task worker
uvicorn app.main:app --reload & celery -A app.tasks.celery_app.celery_app worker --loglevel=info &

# 5. Start Next.js frontend application
cd ../frontend && npm install && npm run dev
```

---

## Environment Variables

| Variable | Description | Default / Example |
| :--- | :--- | :--- |
| `DATABASE_URL` | Async connection string for SQLAlchemy. | `postgresql+asyncpg://postgres:postgres@localhost:5432/resume` |
| `SECRET_KEY` | Key used for signing JWT login tokens. | `your_secret_signing_key` |
| `ENCRYPTION_KEY` | 32-byte Fernet key for encrypting provider keys. | `3kR5mR_y6Wk7W5P_l7B1D_g9B2v9f9r7a6S5D4f3g2h=` |
| `REDIS_URL` | Task broker message queue and GitHub API cache. | `redis://localhost:6379/0` |
| `GOOGLE_CLIENT_ID` | Google OAuth Client ID. | `oauth-client-id.apps.googleusercontent.com` |
| `STRIPE_API_KEY` | Payment API key for Pro checkout. | `sk_test_...` |
| `AWS_ACCESS_KEY_ID`| AWS S3 storage access key (falls back to local storage if empty) | `AKIA...` |

---

## Deployment Checklist

### Frontend (Vercel)
- Set environment `NEXT_PUBLIC_API_URL` pointing to your Railway backend API route.
- Configure CORS origin settings inside Vercel Dashboard.

### Backend (Railway)
- Connect Railway GitHub repository integration.
- Ensure the Docker builder executes using the custom `Dockerfile` containing XeLaTeX.
- Set up DB migrations: run `alembic upgrade head` before serving production endpoints.
- Configure Stripe Webhook endpoints pointing to `/api/v1/billing/webhook`.
