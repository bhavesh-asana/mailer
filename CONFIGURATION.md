# Development vs Production Configuration

## Development Settings (default)

The default `settings.py` is configured for development with:
- `DEBUG = True` (enables Django debug toolbar and proper static file serving)
- `CORS_ALLOW_ALL_ORIGINS = True` (allows all origins for frontend development)
- No HTTPS enforcement (works with HTTP for local development)
- Relaxed session/CSRF cookie settings
- No rate limiting (easier for testing)

## Production Settings

Use `settings_production.py` for production deployment:

```bash
# Production deployment
python manage.py runserver --settings=mailer.settings_production
```

Or set environment variable:
```bash
export DJANGO_SETTINGS_MODULE=mailer.settings_production
```

### Production Features:
- `DEBUG = False`
- HTTPS enforcement
- Strict CORS policy
- Secure cookie settings
- Rate limiting enabled
- Comprehensive logging
- PostgreSQL database support
- Static file optimization

## Quick Switch for Testing

### Development Mode (default):
```bash
python manage.py runserver
# Admin at: http://127.0.0.1:8000/admin/
```

### Production Mode:
```bash
python manage.py runserver --settings=mailer.settings_production
# Requires HTTPS in production
```

## Environment Variables

### Development (.env):
```bash
DEBUG=True
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
USE_TLS=True
```

### Production (.env):
```bash
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,api.yourdomain.com
DATABASE_URL=postgresql://user:pass@host:port/dbname
FRONTEND_URL=https://yourdomain.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
USE_TLS=True
```

This setup ensures:
- ✅ **Development**: Easy setup, all features work, admin styling loads properly
- ✅ **Production**: Secure, optimized, enterprise-ready configuration
