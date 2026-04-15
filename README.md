# URL Shortener API

A high-performance, production-ready REST API built with FastAPI that transforms long URLs into concise, shareable short links. Features include user authentication, click analytics, automatic link expiration, rate limiting, and background cleanup tasks.

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [Project Architecture](#project-architecture)
- [Installation & Setup](#installation--setup)
- [API Endpoints](#api-endpoints)
- [Usage Examples](#usage-examples)
- [Advanced Features](#advanced-features)
- [Testing](#testing)
- [Project Structure](#project-structure)

---

## 🎯 Overview

**URL Shortener API** is a modern REST API that simplifies URL management by:
- Converting lengthy URLs into short, memorable codes
- Tracking click analytics and user engagement
- Managing link lifecycle with automatic expiration
- Implementing intelligent rate limiting to prevent abuse
- Providing comprehensive user authentication

Perfect for social media, marketing campaigns, tracking links, or any scenario where URL sharing needs to be efficient and trackable.

---

## ✨ Key Features

### **URL Shortening**
- ✅ Generate unique 6-character short codes (customizable length)
- ✅ Duplicate code detection and collision handling
- ✅ Configurable link expiration (default: 30 days)
- ✅ Direct redirect with HTTP 302 response
- ✅ Support for any valid long URL

### **User Authentication**
- ✅ User registration with email validation
- ✅ Secure password hashing with bcrypt
- ✅ JWT-based token authentication
- ✅ 30-minute token expiration window
- ✅ Token validation on protected routes

### **Analytics & Tracking**
- ✅ Click counting on shortened links
- ✅ Per-user analytics dashboard
- ✅ Most clicked URL identification
- ✅ Link performance metrics
- ✅ Creation and modification timestamps

### **Advanced Capabilities**
- ✅ Rate limiting (5 requests per 60 seconds per user)
- ✅ Redis-backed rate limiting with TTL
- ✅ Automatic cleanup of expired links
- ✅ Background job scheduler (24-hour cycle)
- ✅ CORS support for cross-origin requests

### **Data Management**
- ✅ PostgreSQL database with SQLAlchemy ORM
- ✅ User-URL relationship tracking
- ✅ Database connection pooling
- ✅ Automated migration support
- ✅ Comprehensive data persistence

---

## 🛠️ Technology Stack

| Component | Technology |
|-----------|-----------|
| **Framework** | FastAPI 0.104+ |
| **Python Version** | Python 3.8+ |
| **Database** | PostgreSQL |
| **ORM** | SQLAlchemy |
| **Authentication** | JWT, bcrypt, python-jose |
| **Caching/Rate Limit** | Redis |
| **Scheduler** | APScheduler |
| **Validation** | Pydantic |
| **Testing** | pytest |
| **Server** | Uvicorn |

### Key Dependencies:
```
fastapi==0.104.1
sqlalchemy==2.0.0
psycopg2-binary
python-jose[cryptography]
bcrypt
redis
apscheduler
pydantic[email]
python-multipart
```

---

## 🏗️ Project Architecture

```
URL-SHORTENER/
├── app/
│   ├── __init__.py
│   ├── main.py                        # FastAPI app & route handlers
│   ├── models.py                      # SQLAlchemy ORM models
│   ├── database.py                    # Database configuration
│   ├── utils.py                       # Utility functions
│   ├── auths/
│   │   └── auth.py                    # Authentication logic (JWT, bcrypt)
│   ├── schemas/
│   │   └── schema.py                  # Pydantic validation schemas
│   ├── services/
│   │   ├── cleanup_service.py         # Expired link cleanup
│   │   └── rate_limiting_service.py   # Rate limiting logic
│   └── schedular/
│       └── background_job.py          # Background scheduler setup
├── tests/
│   ├── __init__.py
│   └── test_cleanup.py                # Unit tests for cleanup service
├── .env.example                       # Environment template
├── requirements.txt                   # Python dependencies
└── README.md                          # This file
```

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- Redis 6+
- Git

### Step-by-Step Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/muhammads-git/URL-SHORTENER.git
   cd URL-SHORTENER
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create `.env` file:**
   ```bash
   cp .env.example .env
   ```

5. **Configure environment variables:**
   ```env
   # Database
   DATABASE_URL=postgresql://user:password@localhost:5432/url_shortener

   # JWT
   SECRET_KEY=your-secret-key-here
   ALGORITHM=HS256

   # Redis
   REDIS_HOST=localhost
   REDIS_PORT=6379
   ```

6. **Initialize database:**
   ```bash
   # Create database tables (automatic with FastAPI startup)
   python -c "from app.database import engine, Base; Base.metadata.create_all(bind=engine)"
   ```

7. **Start Redis server** (in separate terminal):
   ```bash
   redis-server
   ```

8. **Start the API server:**
   ```bash
   uvicorn app.main:app --reload
   ```

   API available at: `http://localhost:8000`
   Interactive docs: `http://localhost:8000/docs`

---

## 📡 API Endpoints

### **Authentication Endpoints**

#### Register User
```http
POST /register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePassword123!"
}
```

**Response:**
```json
{
  "success": true,
  "message": "User created!"
}
```

---

#### Login
```http
POST /login
Content-Type: application/x-www-form-urlencoded

username=john_doe&password=SecurePassword123!
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

### **URL Shortening Endpoints**

#### Create Short URL
```http
POST /url_shortener
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: application/x-www-form-urlencoded

long_url=https://www.example.com/very/long/url&valid_days=30
```

**Response:**
```json
{
  "shortUrl": "http://localhost:8000/aBc123",
  "code": "aBc123",
  "longUrl": "https://www.example.com/very/long/url"
}
```

**Parameters:**
- `long_url` (required): The URL to shorten
- `valid_days` (optional): Link validity in days (default: 30)

---

#### Redirect to Original URL
```http
GET /{short_code}
```

**Behavior:**
- Returns HTTP 302 redirect to original URL
- Increments click counter
- Returns 404 if short code not found
- Returns 410 if link has expired

**Example:**
```bash
curl -L http://localhost:8000/aBc123
# Redirects to original URL
```

---

### **Analytics Endpoints**

#### Get User Analytics
```http
GET /analytics
Authorization: Bearer YOUR_ACCESS_TOKEN
```

**Response:**
```json
{
  "most_clicked": {
    "long_url": "https://github.com/muhammads-git",
    "short_url": "aBc123",
    "clicks": 45
  },
  "all_links": [
    {
      "long_url": "https://github.com/muhammads-git",
      "short_code": "aBc123",
      "clicks": 45
    },
    {
      "long_url": "https://twitter.com/muhammads",
      "short_code": "xYz789",
      "clicks": 12
    }
  ]
}
```

---

## 💡 Usage Examples

### **Using cURL**

1. **Register:**
   ```bash
   curl -X POST http://localhost:8000/register \
     -H "Content-Type: application/json" \
     -d '{
       "username": "testuser",
       "email": "test@example.com",
       "password": "Password123!"
     }'
   ```

2. **Login:**
   ```bash
   curl -X POST http://localhost:8000/login \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=testuser&password=Password123!"
   ```

3. **Create Short URL:**
   ```bash
   TOKEN="your_access_token_here"
   curl -X POST http://localhost:8000/url_shortener \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "long_url=https://www.python.org&valid_days=30"
   ```

4. **View Analytics:**
   ```bash
   curl -X GET http://localhost:8000/analytics \
     -H "Authorization: Bearer $TOKEN"
   ```

### **Using Python Requests**

```python
import requests

BASE_URL = "http://localhost:8000"

# Register
response = requests.post(f"{BASE_URL}/register", json={
    "username": "testuser",
    "email": "test@example.com",
    "password": "Password123!"
})
print(response.json())

# Login
login_response = requests.post(
    f"{BASE_URL}/login",
    data={"username": "testuser", "password": "Password123!"}
)
token = login_response.json()["access_token"]

# Create short URL
headers = {"Authorization": f"Bearer {token}"}
shorten_response = requests.post(
    f"{BASE_URL}/url_shortener",
    data={"long_url": "https://www.example.com/very/long/url", "valid_days": 30},
    headers=headers
)
print(shorten_response.json())

# Get analytics
analytics = requests.get(f"{BASE_URL}/analytics", headers=headers)
print(analytics.json())
```

---

## 🔬 Advanced Features

### **Rate Limiting**

The API implements intelligent rate limiting to protect against abuse:

- **Limit:** 5 requests per 60 seconds
- **Identifier:** User ID (if authenticated) or IP address
- **Storage:** Redis for fast lookups
- **TTL:** Automatic expiration after time window

**Rate Limit Exceeded Response:**
```json
{
  "detail": "Rate limit exceeded, please try again in 45 seconds."
}
```

**HTTP Status:** 429 (Too Many Requests)

---

### **Automatic Link Expiration**

Links automatically expire after the specified validity period:

- **Default:** 30 days
- **Customizable:** Per-link basis (1-365 days)
- **Automatic Cleanup:** Every 24 hours via background scheduler
- **Expired Link Response:** HTTP 410 (Gone)

---

### **Background Job Scheduler**

A background job runs every 24 hours to clean up expired links:

```python
# Runs automatically on startup
# Deletes expired URLs from database
# Logs cleanup operations
# Continues running in background
```

---

## 🧪 Testing

### **Run Unit Tests**

```bash
pytest tests/
```

### **Test Coverage**

The project includes comprehensive tests for the cleanup service:

```bash
pytest tests/test_cleanup.py -v
```

### **Test Examples**

**File:** `tests/test_cleanup.py`

- `test_cleanup_deletes_expired_link()` - Verifies expired links are removed
- `test_cleanup_keeps_valid_link()` - Confirms valid links are preserved

---

## 📊 Database Schema

### **users Table**
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR UNIQUE NOT NULL,
    email VARCHAR UNIQUE NOT NULL,
    password VARCHAR NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **urls Table**
```sql
CREATE TABLE urls (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    long_url VARCHAR NOT NULL,
    short_url VARCHAR UNIQUE NOT NULL,
    clicks INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP + INTERVAL '30 days'),
    user_id INTEGER FOREIGN KEY REFERENCES users(id)
);
```

---

## 🔐 Security Features

- **Password Hashing:** bcrypt with salting
- **Token-Based Auth:** JWT with expiration
- **Rate Limiting:** Redis-backed abuse prevention
- **Input Validation:** Pydantic schemas
- **CORS:** Configurable cross-origin access

---

## 📝 Data Models

### **User Model**
```python
class User(Base):
    __tablename__ = "users"
    
    id: int                    # Primary key
    username: str              # Unique username
    email: str                 # Unique email
    password: str              # Hashed password
    created_at: datetime       # Registration timestamp
    urls: List[Url]           # Related shortened URLs
```

### **URL Model**
```python
class Url(Base):
    __tablename__ = "urls"
    
    id: int                    # Primary key
    long_url: str             # Original URL
    short_url: str            # Unique short code
    clicks: int               # Click counter
    created_at: datetime      # Creation timestamp
    expires_at: datetime      # Expiration timestamp
    user_id: int              # Owner user ID
    owner: User               # Related user
```

---

## 📋 Environment Variables

```env
# Database Connection
DATABASE_URL=postgresql://user:password@localhost:5432/url_shortener

# JWT Configuration
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

---

## 🚀 Deployment

### **Docker Deployment**

Create a `Dockerfile`:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t url-shortener .
docker run -p 8000:8000 --env-file .env url-shortener
```

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is open source and available under the MIT License.

---

## 👤 Author

**Muhammad S** - [GitHub Profile](https://github.com/muhammads-git)

---

## 📞 Support

For issues, questions, or suggestions, please open an issue on the [GitHub repository](https://github.com/muhammads-git/URL-SHORTENER/issues).

---

## 🗺️ Roadmap

- [ ] Custom short codes (e.g., `/my-awesome-link`)
- [ ] QR code generation
- [ ] Advanced analytics dashboard
- [ ] Bulk URL shortening
- [ ] API usage statistics
- [ ] Link password protection
- [ ] Mobile app integration

---

**Last Updated:** April 14, 2026  
**Framework:** FastAPI  
**Python Version:** 3.8+
