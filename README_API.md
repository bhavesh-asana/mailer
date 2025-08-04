# Mailer Service REST API

A Django-based REST API for sending emails with support for templates, bulk emails, and comprehensive logging.

## Features

- ✅ Send single emails via REST API
- ✅ Send bulk emails with template variables
- ✅ Email templates management
- ✅ Recipient management
- ✅ Email campaign tracking
- ✅ Comprehensive email logging
- ✅ Multiple SMTP configuration support
- ✅ Swagger API documentation
- ✅ Django admin interface

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and update with your email settings:

```bash
cp .env.example .env
```

Update the following variables in `.env`:
```
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
USE_TLS=True
```

### 3. Run Migrations

```bash
python manage.py migrate
```

### 4. Create Default Email Configuration

```bash
python manage.py setup_default_email_config
```

### 5. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 6. Start the Server

```bash
python manage.py runserver
```

## API Endpoints

### Core Email Sending

- **POST** `/api/send-email/` - Send a single email
- **POST** `/api/send-bulk-email/` - Send bulk emails
- **GET** `/api/stats/` - Get email statistics
- **GET** `/api/health/` - Health check

### Management Endpoints

- **GET/POST** `/api/templates/` - Email templates
- **GET/POST** `/api/recipients/` - Recipients management
- **GET/POST** `/api/campaigns/` - Email campaigns
- **GET** `/api/logs/` - Email logs (read-only)
- **GET/POST** `/api/configurations/` - SMTP configurations

### Documentation

- **Swagger UI**: `http://localhost:8000/swagger/`
- **ReDoc**: `http://localhost:8000/redoc/`
- **Django Admin**: `http://localhost:8000/admin/`

## API Usage Examples

### Send a Single Email

```bash
curl -X POST http://localhost:8000/api/send-email/ \
  -H "Content-Type: application/json" \
  -d '{
    "to_email": "recipient@example.com",
    "to_name": "John Doe",
    "subject": "Test Email",
    "body": "Hello, this is a test email!",
    "is_html": false
  }'
```

### Send Bulk Emails

```bash
curl -X POST http://localhost:8000/api/send-bulk-email/ \
  -H "Content-Type: application/json" \
  -d '{
    "recipients": [
      {
        "email": "user1@example.com",
        "name": "User One",
        "variables": {"discount": "20%"}
      },
      {
        "email": "user2@example.com", 
        "name": "User Two",
        "variables": {"discount": "15%"}
      }
    ],
    "subject_template": "Special offer for $name!",
    "body_template": "Hello $name, enjoy $discount off your next purchase!",
    "campaign_name": "Summer Sale 2025"
  }'
```

### Get Email Statistics

```bash
curl http://localhost:8000/api/stats/
```

Response:
```json
{
  "total_sent": 150,
  "total_failed": 5,
  "total_pending": 0,
  "success_rate": 96.77,
  "recent_campaigns": 8
}
```

## Template Variables

The API supports template variables in both subject and body using Python's string.Template format:

- `$name` - Recipient name
- `$email` - Recipient email
- `$company` - Recipient company
- Custom variables from the `variables` field

Example:
```
Subject: "Welcome to our service, $name!"
Body: "Hello $name from $company, welcome to our platform!"
```

## Models Overview

### EmailTemplate
Store reusable email templates with variables support.

### Recipient
Manage email recipients with additional metadata.

### EmailCampaign
Track email campaigns and their status.

### EmailLog
Comprehensive logging of all email activities.

### EmailConfiguration
Multiple SMTP server configurations.

## Authentication

Currently, the API allows anonymous access for email sending endpoints. In production, you should:

1. Change `permission_classes = [AllowAny]` to `[IsAuthenticated]` in views
2. Set up proper authentication (API keys, JWT, etc.)
3. Configure CORS settings appropriately

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SMTP_SERVER` | SMTP server hostname | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP server port | `587` |
| `EMAIL_USERNAME` | SMTP username | Required |
| `EMAIL_PASSWORD` | SMTP password | Required |
| `USE_TLS` | Use TLS encryption | `True` |
| `SECRET_KEY` | Django secret key | Required |
| `DEBUG` | Django debug mode | `False` |

## Production Deployment

For production deployment:

1. Set `DEBUG=False` in settings
2. Configure a proper database (PostgreSQL/MySQL)
3. Set up proper SMTP credentials
4. Use a production WSGI server (Gunicorn)
5. Configure reverse proxy (Nginx)
6. Set up SSL certificates
7. Configure proper authentication and authorization

## Error Handling

The API returns appropriate HTTP status codes:

- `200` - Success
- `400` - Bad Request (validation errors)
- `401` - Unauthorized
- `404` - Not Found
- `500` - Internal Server Error

Error responses include detailed error messages in JSON format.

## Logging

All email activities are logged to:
- Database (EmailLog model)
- Application logs (configured in Django settings)

## Support

For issues and questions, please check the Django admin interface at `/admin/` where you can:

- View email logs
- Manage templates and recipients
- Configure SMTP settings
- Monitor campaign status
