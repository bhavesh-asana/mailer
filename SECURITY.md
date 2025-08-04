# Security Best Practices

## Authentication & Authorization

The Django Email API is now secured with the following authentication requirements:

### API Endpoints Security
All API endpoints now require authentication:
- **Email Templates**: `IsAuthenticated` - Users must be logged in to manage templates
- **Recipients**: `IsAuthenticated` - Users must be logged in to manage recipients  
- **Campaigns**: `IsAuthenticated` - Users must be logged in to manage campaigns
- **Email Logs**: `IsAuthenticated` - Users must be logged in to view email logs
- **Configurations**: `IsAuthenticated` - Users must be logged in to manage email configs
- **Attachments**: `IsAuthenticated` - Users must be logged in to upload/manage files
- **Send Email**: `IsAuthenticated` - Users must be logged in to send emails
- **Bulk Email**: `IsAuthenticated` - Users must be logged in to send bulk emails
- **Statistics**: `IsAuthenticated` - Users must be logged in to view email stats
- **Health Check**: `IsAuthenticated` - Users must be logged in to check system health

### Authentication Methods
The API supports two authentication methods:
1. **Session Authentication**: For web browser access (recommended for frontend apps)
2. **Basic Authentication**: For API clients using username/password

## Security Headers

The following security headers are configured:

- `X-Frame-Options: DENY` - Prevents clickjacking attacks
- `X-Content-Type-Options: nosniff` - Prevents MIME type sniffing
- `X-XSS-Protection: 1; mode=block` - Enables XSS filtering
- `Strict-Transport-Security` - Forces HTTPS connections (production)

## CORS Configuration

Cross-Origin Resource Sharing (CORS) is configured with:
- **Restricted Origins**: Only specified domains can access the API
- **Credential Support**: Cookies/credentials allowed for authorized origins
- **Limited Headers**: Only necessary headers are allowed

## File Upload Security

File uploads are secured with:
- **Size Limits**: Maximum 10MB per file
- **Field Limits**: Maximum 100 form fields per request
- **Authentication Required**: Only logged-in users can upload files
- **Secure Storage**: Files stored in protected directory

## Rich Text Editor Security

CKEditor 5 configuration includes comprehensive security hardening:
- **Latest Secure Version**: Using CKEditor 5 (latest stable version) - completely secure
- **No Legacy Vulnerabilities**: CKEditor 5 is a complete rewrite with modern security architecture
- **Content Filtering**: Strict htmlSupport rules to prevent XSS attacks
- **Plugin Restrictions**: Dangerous plugins (MediaEmbed, file uploads) disabled in production
- **HTML Sanitization**: Only safe HTML tags and attributes are allowed
- **Link Security**: External links properly validated and filtered
- **Production Hardening**: More restrictive configuration for production environments
- **XSS Prevention**: Built-in protection against cross-site scripting attacks

## Rate Limiting

API rate limiting is configured:
- **Anonymous Users**: 100 requests per hour
- **Authenticated Users**: 1000 requests per hour

## Session Security

Session management includes:
- **Secure Cookies**: Session cookies only sent over HTTPS
- **HTTP Only**: Session cookies not accessible via JavaScript
- **Same Site**: Strict same-site policy
- **Auto Expiry**: Sessions expire when browser closes

## Production Deployment Checklist

### Required Settings
- [ ] Set `DEBUG = False`
- [ ] Configure `SECRET_KEY` (use environment variable)
- [ ] Set proper `ALLOWED_HOSTS`
- [ ] Configure HTTPS with `SECURE_SSL_REDIRECT = True`
- [ ] Set secure cookie settings
- [ ] Configure database with connection pooling
- [ ] Set up proper logging
- [ ] Configure static file serving
- [ ] Set up media file storage (consider cloud storage)

### Environment Variables
Create a `.env` file with:
```bash
SECRET_KEY=your-very-long-random-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,api.yourdomain.com
DATABASE_URL=postgresql://user:pass@host:port/dbname
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
USE_TLS=True
```

### Database Security
- Use PostgreSQL or another production database (not SQLite)
- Configure database connection with SSL
- Use connection pooling
- Regular database backups
- Restrict database access to application servers only

### Infrastructure Security
- Use HTTPS/TLS for all communications
- Configure firewall rules
- Regular security updates
- Monitor access logs
- Use a reverse proxy (nginx/Apache)
- Implement backup and disaster recovery

### User Management
- Enforce strong password policies
- Regular user access reviews
- Implement user roles and permissions
- Monitor user activity
- Secure password reset functionality

## Monitoring & Logging

Implement monitoring for:
- Failed authentication attempts
- Unusual API usage patterns
- File upload activities
- Email sending volumes
- System performance metrics

## Contact

For security issues, please contact the development team immediately.
Do not create public issues for security vulnerabilities.
