# PhotoEnhancer - Scalable Django Application

## 🚀 Overview

PhotoEnhancer is now configured as a production-ready, scalable Django application optimized for high-traffic photo enhancement services.

## 📋 What's Been Updated

### 1. Admin Panel Fix ✅
- Removed duplicate `UserProfile` registration that caused `AlreadyRegistered` error
- Enhanced admin interface with:
  - Inline UserProfile and UserSubscription editing
  - Photos count display per user
  - Photo management actions (reprocess, soft delete)
  - Advanced filtering and searching

### 2. Modern Home UI ✅
- **For Non-Authenticated Users**: Beautiful landing page with:
  - Animated hero section with AI showcase
  - Feature highlights (AI Enhancement, Smart Crop, Background Removal, 4K Export)
  - Interactive demo upload section
  - Three-tier pricing cards (Free, Pro $9/mo, Enterprise $49/mo)
  - Responsive design with dark mode support
  - Lucide icons and Tailwind CSS styling

- **For Authenticated Users**: Professional dashboard with:
  - Sidebar navigation
  - Photo editor with step indicators
  - User profile display
  - Dark mode support

### 3. Scalability Improvements

#### Database
- **Upgraded**: SQLite → PostgreSQL (connection pooling, persistent connections)
- Django ORM optimized with indexes on frequently queried fields

#### Caching
- **Redis cache** for session storage and application caching
- Cache middleware for automatic HTTP response caching
- Database query optimization with `select_related` and `prefetch_related`

#### Background Processing
- **Celery** with Redis broker for async photo processing
- Task queue with priority levels and retry logic
- Automatic cleanup jobs:
  - Daily: Remove 30+ day old deleted photos
  - Monthly: Reset user photo quotas
  - Weekly: Storage optimization

#### Security
- **Nginx** reverse proxy with rate limiting
- HTTPS/SSL ready configuration
- CORS headers for frontend integration
- Security headers (HSTS, XSS Protection, Content Security Policy)
- Admin-only endpoints restricted

#### Containerization
- **Docker & Docker Compose** for development and production
- Multi-stage Dockerfile (builder + production)
- Non-root user for security
- Health checks for containers

#### Monitoring
- Structured JSON logging with rotation
- Health check endpoint (`/health/`)
- Admin statistics endpoint (`/api/admin/stats/`)
- Error reporting via email

## 🗂️ Project Structure

```
Backend/
├── accounts/
│   ├── models.py         # User, Photo, Subscription models
│   ├── views.py          # API endpoints
│   ├── admin.py          # Admin configuration
│   ├── tasks.py          # Celery background tasks
│   └── ...
├── photo_enhancer/
│   ├── settings.py       # Production-ready settings
│   ├── urls.py           # URL configuration
│   ├── celery.py         # Celery app configuration
│   └── asgi.py           # ASGI entry point
├── docker-compose.yml    # Production orchestration
├── docker-compose.dev.yml # Development setup
├── Dockerfile           # Container definition
├── nginx.conf           # Web server configuration
├── requirements.txt     # Python dependencies
└── .env.example         # Environment template
```

## 🚀 Quick Start

### Development (Docker - Recommended)

1. **Clone and setup environment:**
```bash
cd Backend
cp .env.example .env
# Edit .env with your values (or use defaults for dev)
```

2. **Start services:**
```bash
docker-compose -f docker-compose.dev.yml up --build
```

3. **Run migrations (first time):**
```bash
docker-compose -f docker-compose.dev.yml exec web python manage.py migrate
docker-compose -f docker-compose.dev.yml exec web python manage.py createsuperuser
```

4. **Access the app:**
- App: http://localhost:8000
- Admin: http://localhost:8000/admin/

### Production

1. **Setup SSL certificates in `ssl/` directory** (or use Let's Encrypt)

2. **Create production environment:**
```bash
cp .env.example .env
# Edit .env with production values:
# - DEBUG=False
# - SECRET_KEY=your-secret-key
# - DATABASE_URL=postgres://user:pass@host/db
# - REDIS_URL=redis://host:6379/1
# - ALLOWED_HOSTS=yourdomain.com
```

3. **Start production services:**
```bash
docker-compose up -d --build
```

4. **Create admin user:**
```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

## 🔧 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/accounts/api/login/` | Login user |
| POST | `/accounts/api/signup/` | Register new user |
| POST | `/accounts/api/logout/` | Logout user |
| GET | `/accounts/api/check-auth/` | Check authentication status |
| GET | `/accounts/api/csrf-token/` | Get CSRF token |

### Photos
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/photos/` | List user's photos |
| POST | `/api/photos/upload/` | Upload new photo |
| GET | `/api/photos/<uuid>/` | Get photo details |
| DELETE | `/api/photos/<uuid>/` | Delete photo |
| GET | `/api/photos/<uuid>/download/` | Download enhanced photo |

### Other
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/subscription/` | Get subscription details |
| GET | `/health/` | Health check |
| GET | `/api/admin/stats/` | Admin statistics (staff only) |

## 📊 Scaling Architecture

```
                    ┌─────────────────┐
                    │    Load Balancer│
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │      Nginx      │ (SSL termination, static files)
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │   Django App    │ (x2 replicas for HA)
                    │   (Gunicorn)    │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
┌───────▼───────┐   ┌───────▼───────┐   ┌───────▼───────┐
│   PostgreSQL  │   │     Redis     │   │Celery Workers │
│   (Database)  │   │(Cache/Queue)  │   │(Processing)   │
└───────────────┘   └───────────────┘   └───────────────┘
```

## 🔐 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | Required |
| `DEBUG` | Debug mode | False |
| `DATABASE_URL` | PostgreSQL connection URL | SQLite |
| `REDIS_URL` | Redis connection URL | Database cache |
| `ALLOWED_HOSTS` | Allowed domain names | localhost |
| `CORS_ALLOWED_ORIGINS` | Frontend origins | localhost |
| `ADMIN_EMAIL` | Admin notifications | admin@localhost |

## 📈 Monitoring

- **Health Check**: `GET /health/` returns service status
- **Admin Stats**: `GET /api/admin/stats/` (requires staff access)
- **Logs**: Check `logs/django.log` for application logs

## 🔧 Maintenance Tasks

Celery Beat automatically runs these tasks:
- **Daily 2 AM**: Cleanup deleted photos older than 30 days
- **1st of month**: Reset monthly photo quotas
- **Sunday 3 AM**: Storage optimization

## 📝 License

This project is now configured for production use with enterprise-grade scalability features.

## 🆘 Troubleshooting

### Admin panel shows "AlreadyRegistered" error
✅ Fixed by removing duplicate `admin.site.register(UserProfile)` in admin.py

### Photos not uploading
- Check `MEDIA_ROOT` and `MEDIA_URL` settings
- Verify storage permissions
- Check file size limits (10MB)

### Celery tasks not running
- Verify Redis is running: `docker-compose logs redis`
- Check worker logs: `docker-compose logs celery_worker`

### Database connection errors
- Check `DATABASE_URL` format: `postgres://user:pass@host:port/db`
- Verify PostgreSQL container is healthy

## 📞 Support

For issues or questions about the scalable configuration:
1. Check the logs: `docker-compose logs -f`
2. Verify environment variables
3. Check health endpoint: `curl http://localhost:8000/health/`
