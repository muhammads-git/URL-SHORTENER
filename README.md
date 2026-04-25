# 🚀 URL Shortener - AI-Powered Smart Slug Generator

An intelligent, high-performance REST API built with **FastAPI** that transforms long URLs into semantic, AI-generated short slugs. Instead of random codes, this system extracts page titles using **Beautiful Soup**, analyzes them with **Groq AI**, and generates meaningful short codes asynchronously with full analytics, authentication, and rate limiting.

---

## 📋 Table of Contents

- [Overview](#overview)
- [✨ What's New - AI Features](#whats-new---ai-features)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [How AI Slug Generation Works](#how-ai-slug-generation-works)
- [Project Architecture](#project-architecture)
- [Installation & Setup](#installation--setup)
- [API Endpoints](#api-endpoints)
- [Usage Examples](#usage-examples)
- [Advanced Features](#advanced-features)
- [Testing](#testing)
- [Environment Variables](#environment-variables)
- [Deployment](#deployment)

---

## 🎯 Overview

**URL Shortener with AI Slug Generation** is a revolutionary URL management system that combines intelligent AI with traditional URL shortening. Instead of random character codes, your shortened URLs now have **semantic meaning** derived from the page content.

**Key Workflow:**
1. User submits a long URL
2. System fetches the page and extracts the title using **Beautiful Soup**
3. AI analyzes the title and generates a meaningful, SEO-friendly slug
4. Slug is stored with analytics tracking, auto-expiration, and click counting
5. Asynchronous processing ensures zero-blocking performance

Perfect for branding campaigns, marketing links, documentation, or anywhere meaningful URLs enhance user experience.

---

## ✨ What's New - AI Features

### 🤖 AI-Powered Slug Generation
- **Intelligent Slugs:** Instead of random codes like `abc123`, generate meaningful slugs like `python-docs` or `github-repo`
- **Groq AI Integration:** Leverages state-of-the-art LLaMA 3.3 70B model for intelligent slug creation
- **Content-Aware:** AI reads page titles to understand context and generate relevant slugs
- **Fallback Handling:** If AI fails or URL is unreachable, system gracefully falls back to random code generation

### 🕷️ Beautiful Soup Web Scraping
- **Title Extraction:** Automatically fetches and parses HTML to extract page titles
- **Async Scraping:** Non-blocking HTTP requests using `httpx` for lightning-fast performance
- **Error Resilience:** Handles network timeouts, missing titles, and invalid URLs gracefully
- **User-Agent Support:** Identifies as a proper bot to avoid blocking

### ⚡ Asynchronous Architecture
- **Non-Blocking Operations:** All AI and scraping operations run asynchronously
- **Concurrent Processing:** Handle multiple URL shortening requests simultaneously
- **Efficient Resource Usage:** No thread blocking, pure async/await Python
- **Fast Responses:** Users get instant feedback while background tasks complete

---

## ✨ Key Features

### **AI-Driven URL Shortening**
- ✅ Generate semantic, meaningful short slugs using AI
- ✅ Automatic page title extraction via Beautiful Soup
- ✅ Fallback to random codes if AI fails
- ✅ Intelligent slug collision detection
- ✅ Asynchronous processing for instant response times

### **Smart Slug Generation Pipeline**
- ✅ **Step 1:** Fetch URL with asyncio and beautiful soup
- ✅ **Step 2:** Extract page title
- ✅ **Step 3:** Send title to Groq AI for slug generation
- ✅ **Step 4:** Check for slug collision in database
- ✅ **Step 5:** Store with 30-day TTL (customizable)

### **User Authentication & Security**
- ✅ User registration with email validation
- ✅ Secure password hashing with bcrypt
- ✅ JWT-based token authentication
- ✅ 30-minute token expiration
- ✅ Token validation on protected routes

### **Analytics & Tracking**
- ✅ Click counting on shortened links
- ✅ Per-user analytics dashboard
- ✅ Most clicked URL identification
- ✅ Link performance metrics
- ✅ Creation and expiration timestamps

### **Advanced Capabilities**
- ✅ Rate limiting (5 requests per 60 seconds per user)
- ✅ Redis-backed caching for ultra-fast redirects
- ✅ Automatic link expiration (1-365 days, default 30)
- ✅ Background job scheduler (24-hour cleanup cycle)
- ✅ QR code generation for shortened URLs
- ✅ CORS support for cross-origin requests

### **Data Management**
- ✅ PostgreSQL with SQLAlchemy ORM
- ✅ User-URL relationship tracking
- ✅ Database connection pooling
- ✅ Automated migrations
- ✅ Comprehensive data persistence

---

## 🛠️ Technology Stack

| Component | Technology |
|-----------|-----------|
| **Framework** | FastAPI 0.104+ |
| **Python Version** | Python 3.8+ |
| **AI Model** | Groq API (LLaMA 3.3 70B) |
| **Web Scraping** | Beautiful Soup 4, httpx |
| **Async Runtime** | asyncio |
| **Database** | PostgreSQL |
| **ORM** | SQLAlchemy 2.0+ |
| **Authentication** | JWT, bcrypt, python-jose |
| **Caching/Rate Limit** | Redis 6+ |
| **Job Scheduler** | APScheduler |
| **QR Codes** | qrcode, Pillow |
| **Validation** | Pydantic |
| **Testing** | pytest |
| **Server** | Uvicorn |

### Key Dependencies:
