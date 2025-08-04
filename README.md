# Mailer Service - Django REST API

A production-ready Django REST API for email sending with comprehensive features including templates, bulk emails, campaign tracking, and detailed logging.

## 🚀 Quick Start

### 1. Installation

```bash
git clone <repository-url>
cd mailer
pip install -r requirements.txt
```

### 2. Configuration

Copy the environment template and configure your email settings:

```bash
cp .env.example .env
```

Update `.env` with your SMTP settings:
```
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
USE_TLS=True
```

### 3. Database Setup (SQLite - No external database required)

```bash
python manage.py migrate
python manage.py setup_default_email_config
python manage.py createsuperuser  # Optional
```

### 4. Run the Server

```bash
python manage.py runserver
```

**Or use the automated setup script:**

```bash
./setup.sh
```

Visit `http://127.0.0.1:8000/swagger/` for interactive API documentation.

## 📋 Features

- ✅ **REST API** - Send emails via HTTP requests
- ✅ **SQLite Database** - No external database setup required
- ✅ **Bulk Email Support** - Send personalized emails to multiple recipients
- ✅ **Bulk Import Recipients** - Import recipients from CSV/Excel files (Admin + CLI)
- ✅ **Email Templates** - Reusable templates with variable substitution
- ✅ **Campaign Tracking** - Monitor email campaign performance
- ✅ **Comprehensive Logging** - Track all email activities
- ✅ **Multiple SMTP Configs** - Support for different email providers
- ✅ **Django Admin** - Web-based management interface
- ✅ **Swagger Documentation** - Auto-generated API docs
- ✅ **Template Variables** - Dynamic content with `$name`, `$email`, etc.

## 🛠 API Endpoints

### Core Functionality
- `POST /api/send-email/` - Send single email
- `POST /api/send-bulk-email/` - Send bulk emails with templates
- `GET /api/stats/` - Email statistics
- `GET /api/health/` - Service health check

### Management
- `/api/templates/` - Email template management
- `/api/recipients/` - Recipient management
- `/api/campaigns/` - Email campaign tracking
- `/api/logs/` - Email activity logs
- `/api/configurations/` - SMTP configuration management

### Bulk Operations
- **Admin Interface** - Bulk import recipients from CSV/Excel files
- **CLI Command** - `python manage.py import_recipients <file> [--dry-run] [--update-existing]`

### Documentation
- `/swagger/` - Interactive API documentation
- `/redoc/` - Alternative API documentation
- `/admin/` - Django admin interface

## 📖 Documentation

Comprehensive documentation is available in the [Wiki](../../wiki):

- **[API Reference](../../wiki/README_API.md)** - Complete API documentation
- **[Installation Guide](../../wiki/Installation.md)** - Detailed setup instructions
- **[Configuration](../../wiki/Configuration.md)** - Configuration options
- **[Quick Start Tutorial](../../wiki/Quick-Start-Tutorial.md)** - Step-by-step tutorial
- **[Code Examples](../../wiki/Code-Examples.md)** - Usage examples
- **[Gmail Setup](../../wiki/GMAIL_SETUP.md)** - Gmail configuration guide
- **[Security Best Practices](../../wiki/Security-Best-Practices.md)** - Security guidelines
- **[Troubleshooting](../../wiki/Troubleshooting.md)** - Common issues and solutions
- **[FAQ](../../wiki/FAQ.md)** - Frequently asked questions

## 🔧 Project Structure

```
mailer/
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
├── .env.example             # Environment template
├── mailer/                  # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── email_api/               # Main email API app
    ├── models.py            # Database models
    ├── views.py             # API views
    ├── serializers.py       # API serializers
    ├── urls.py              # URL routing
    ├── admin.py             # Django admin config
    ├── email_service.py     # Core email functionality
    └── management/          # Management commands
        └── commands/
            └── setup_default_email_config.py
```

## 🚀 Quick API Usage

### Send a Single Email
```bash
curl -X POST http://localhost:8000/api/send-email/ 
  -H "Content-Type: application/json" 
  -d '{
    "to_email": "user@example.com",
    "subject": "Hello World",
    "body": "This is a test email!"
  }'
```

### Send Bulk Emails
```bash
curl -X POST http://localhost:8000/api/send-bulk-email/ 
  -H "Content-Type: application/json" 
  -d '{
    "recipients": [
      {"email": "user1@example.com", "name": "User 1"},
      {"email": "user2@example.com", "name": "User 2"}
    ],
    "subject_template": "Hello $name!",
    "body_template": "Welcome $name to our service!"
  }'
```

## 🔒 Security Notes

- Change `AllowAny` permissions to `IsAuthenticated` in production
- Use environment variables for sensitive configuration
- Set up proper CORS settings
- Use HTTPS in production
- Consider API rate limiting

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the terms specified in the [LICENSE](LICENSE) file.

## 🆘 Support

- Check the [Wiki documentation](../../wiki)
- Review [Troubleshooting guide](../../wiki/Troubleshooting.md)
- Check [FAQ](../../wiki/FAQ.md)
- Open an issue for bugs or feature requests


## Usage Examples

### Send Single Email with Attachment

```python
from mail import EmailSender, EmailConfig, EmailData

config = EmailConfig(
    smtp_server="smtp.gmail.com",
    smtp_port=587,
    username="your_email@gmail.com",
    password="your_app_password",
    use_tls=True
)

sender = EmailSender(config)

email_data = EmailData(
    to_email="recipient@example.com",
    subject="Test Email",
    body="Hello! This is a test email.",
    attachments=["document.pdf", "image.jpg"]
)

success = sender.send_single_email(email_data)
```

### Send Bulk Emails from CSV

```python
results = sender.send_bulk_emails(
    recipients_csv="recipients.csv",
    subject_template="Hello {name}!",
    body_template="Dear {name}, greetings from {company}!",
    attachments=["brochure.pdf"],
    time_interval=10  # 10 seconds between emails
)
```

## CSV File Format

The CSV file should have at minimum an 'email' column. Additional columns can be used in templates:

```csv
email,name,company,position
john.doe@example.com,John Doe,Tech Solutions,Developer
jane.smith@example.com,Jane Smith,Design Co,Designer
```

## Email Templates

Use placeholders in your email templates that match CSV column names:

- Subject: `"Hello {name} from {company}"`
- Body: `"Dear {name}, your position as {position} at {company} is important to us."`

## Security Best Practices

1. **Use App Passwords**: For Gmail, enable 2FA and create an App Password
2. **Environment Variables**: Store credentials in environment variables:
   ```python
   config = EmailConfig(
       smtp_server=os.getenv("SMTP_SERVER"),
       smtp_port=int(os.getenv("SMTP_PORT")),
       username=os.getenv("EMAIL_USERNAME"),
       password=os.getenv("EMAIL_PASSWORD"),
       use_tls=True
   )
   ```

3. **Never commit credentials** to version control

## SMTP Configuration Examples

### Gmail
```python
config = EmailConfig(
    smtp_server="smtp.gmail.com",
    smtp_port=587,
    username="your_email@gmail.com",
    password="your_app_password",  # App Password required
    use_tls=True
)
```

### Outlook/Hotmail
```python
config = EmailConfig(
    smtp_server="smtp-mail.outlook.com",
    smtp_port=587,
    username="your_email@outlook.com",
    password="your_password",
    use_tls=True
)
```

### Yahoo
```python
config = EmailConfig(
    smtp_server="smtp.mail.yahoo.com",
    smtp_port=587,
    username="your_email@yahoo.com",
    password="your_app_password",  # App Password required
    use_tls=True
)
```

## Logging

The application creates detailed logs in `email_sender.log` and displays progress in the console. Log levels include:
- INFO: Successful operations and progress updates
- WARNING: Non-critical issues (missing files, etc.)
- ERROR: Failed operations and errors

## Error Handling

The application includes comprehensive error handling for:
- SMTP connection failures
- Invalid email addresses
- Missing attachment files
- CSV file reading errors
- Network timeouts

## Files

- `mail.py` - Main email sender implementation
- `example_usage.py` - Usage examples
- `recipients.csv` - Sample CSV file with recipient data
- `email_config.example` - Configuration examples
- `requirements.txt` - Optional dependencies
- `README.md` - This documentation

## Customization

You can extend the `EmailSender` class to add features like:
- HTML email support
- Email scheduling
- Bounce handling
- Analytics and tracking
- Custom authentication methods

## Troubleshooting

1. **Authentication failures**: Check username/password and use App Passwords for Gmail
2. **Connection timeouts**: Verify SMTP server and port settings
3. **Attachment errors**: Ensure file paths are correct and files exist
4. **CSV parsing issues**: Check CSV format and encoding (use UTF-8)

For more examples, see `example_usage.py`.
