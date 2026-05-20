# URL Shortener API

A production-grade URL shortening REST API built with FastAPI. Short codes are generated instantly on request and upgraded asynchronously to AI-generated slugs derived from page content — so users get a working link immediately without waiting for AI processing.

---

## Architecture Overview

```
POST /url
    ↓
Generate tmp_code instantly → return to user (<50ms)
    ↓
Enqueue background job (ARQ + Redis)
    ↓
Worker scrapes page title (BeautifulSoup)
Worker calls Groq AI → generates semantic slug
Worker updates DB record with slug
```

**Two-layer Redis cache:**
```
lookup:{short_code} → row_id
url:{row_id}        → long_url
```

Both codes (tmp and slug) point to the same row ID. One source of truth. Cache invalidates automatically when URL TTL expires.

---

## Tech Stack

| Layer | Technology | Why |
|---|---|---|
| Framework | FastAPI | Async support, automatic docs |
| Database | PostgreSQL + SQLAlchemy | Relational data, ORM migrations |
| Cache | Redis | Sub-millisecond lookups, TTL support |
| Task Queue | ARQ | Async jobs, Redis-backed durability |
| Scheduler | APScheduler | Periodic cleanup of expired URLs |
| AI | Groq API (LLaMA 3.3 70B) | Slug generation from page titles |
| Scraping | BeautifulSoup + httpx | Page title extraction |
| Auth | JWT + bcrypt | Stateless authentication |
| Migrations | Alembic | Schema version control |

---

## Key Design Decisions

**Why ARQ instead of calling AI directly in the route?**
AI calls take 2-3 seconds and can fail. Putting them in the request path would block the user and cause failures if Groq is down. ARQ absorbs failures gracefully — jobs persist in Redis even if the worker crashes and are processed when it restarts.

**Why two-layer cache instead of caching by short code?**
A URL has two codes (tmp_code and slug). Caching by code would store the same long URL twice. Two-layer design stores the URL once under the row ID — both codes are lightweight pointers to the same value. Update one Redis key, both codes serve the new URL.

**Why APScheduler for cleanup instead of ARQ?**
ARQ handles user-triggered jobs with no fixed schedule. Expired URL cleanup is a time-driven maintenance task with no user involvement — APScheduler is the right tool.

**Why 302 instead of 301 for redirects?**
301 is cached permanently by browsers. If a user updates their URL destination, browsers that cached the 301 never see the change. 302 ensures the browser always asks your server — you stay in control of the redirect.

---

## Project Structure

```
app/
├── main.py              # App setup, router registration
├── models.py            # SQLAlchemy models
├── database.py          # DB connection and session
├── lifespan.py          # Startup/shutdown (Redis pool)
├── worker.py            # ARQ background tasks
├── utils.py             # Helper functions
├── routers/
│   ├── urls.py          # URL creation, redirect
│   ├── auth.py          # Register, login
│   └── analytics.py     # Analytics, QR code
├── services/
│   ├── ai_service.py        # Groq AI integration
│   ├── scraper_service.py   # Page title scraping
│   ├── rate_limiting_service.py
│   └── qrcode.py
├── schemas/
│   └── schema.py        # Pydantic models
├── schedular/
│   └── background_job.py    # APScheduler cleanup
└── auths/
    └── auth.py          # JWT, password hashing
alembic/                 # DB migrations
tests/                   # pytest
```

---

## Setup & Installation

**Requirements:** Python 3.8+, PostgreSQL, Redis

```bash
# Clone
git clone https://github.com/muhammads-git/URL-SHORTENER.git
cd URL-SHORTENER

# Virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Environment variables
cp .env.example .env
# Fill in your values (see Environment Variables section)

# Run database migrations
alembic upgrade head

# Start Redis (must be running)
# Windows: start Memurai
# Linux/Mac: redis-server

# Start the API
uvicorn app.main:app --reload

# Start the ARQ worker (separate terminal)
python -m arq app.worker.WorkerSettings
```

---

## Environment Variables

```env
DATABASE_URL=postgresql://user:password@localhost/urlshortener
SECRET_KEY=your-jwt-secret-key
GROQ_API_KEY=your-groq-api-key
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
```

---

## API Endpoints

### Authentication
```
POST /auth/register     Register new user
POST /auth/login        Login, returns JWT token
```

### URL Management
```
POST /url               Create short URL (auth required)
GET  /{short_code}      Redirect to original URL
GET  /qrcode/{code}     Generate QR code for URL
```

### Analytics
```
GET  /analytics         User's URL stats and click counts (auth required)
```

---

## Usage Example

**Create a short URL:**
```bash
curl -X POST http://localhost:8000/url \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "long_url=https://github.com/muhammads-git" \
  -F "valid_days=30"
```

**Response:**
```json
{
  "shortUrl": "http://localhost:8000/xK9mPq",
  "tmp_code": "xK9mPq",
  "longUrl": "https://github.com/muhammads-git"
}
```

The tmp_code works immediately. Within seconds, the worker upgrades it to a slug like `github-muhammads` — both codes redirect to the same destination.

---

## Rate Limiting

5 requests per 60 seconds per user on protected routes. Implemented with Redis counters — no database involvement.

---

## URL Expiry

URLs expire after the configured `valid_days` (default 30, max 365). Expiry is synced between PostgreSQL and Redis TTL — expired URLs fade from cache automatically. APScheduler runs cleanup every 24 hours to purge expired records from the database.

---

## Running Tests

```bash
pytest tests/
```