# Configuration Guide

This guide covers how to configure the Email Mailer Application with different email providers and security settings.

## 🔧 Basic Configuration

The mailer application requires SMTP configuration to send emails. You can configure it in several ways:

### Method 1: Direct Configuration (Testing Only)

```python
from mail import EmailConfig

config = EmailConfig(
    smtp_server="smtp.gmail.com",
    smtp_port=587,
    username="your_email@gmail.com",
    password="your_app_password",
    use_tls=True
)
```

### Method 2: Environment Variables (Recommended)

Create a `.env` file in your project directory:

```env
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
USE_TLS=true
```

Then use it in your code:

```python
import os
from mail import EmailConfig

config = EmailConfig(
    smtp_server=os.getenv("SMTP_SERVER"),
    smtp_port=int(os.getenv("SMTP_PORT")),
    username=os.getenv("EMAIL_USERNAME"),
    password=os.getenv("EMAIL_PASSWORD"),
    use_tls=os.getenv("USE_TLS", "true").lower() == "true"
)
```

## 📧 Email Provider Configurations

### Gmail Configuration

**Requirements:**
- Google Account with 2-Factor Authentication enabled
- App Password generated (not your regular password)

**Settings:**
```python
config = EmailConfig(
    smtp_server="smtp.gmail.com",
    smtp_port=587,
    username="your_email@gmail.com",
    password="your_16_character_app_password",
    use_tls=True
)
```

**Setup Steps:**
1. Follow the **[Gmail Setup Guide](Gmail-Setup.md)**
2. Enable 2-Factor Authentication
3. Generate an App Password
4. Use the App Password in your configuration

### Outlook/Hotmail Configuration

**Requirements:**
- Microsoft Account
- Regular password (no app password needed)

**Settings:**
```python
config = EmailConfig(
    smtp_server="smtp-mail.outlook.com",
    smtp_port=587,
    username="your_email@outlook.com",
    password="your_regular_password",
    use_tls=True
)
```

### Yahoo Mail Configuration

**Requirements:**
- Yahoo Account with 2-Factor Authentication
- App Password generated

**Settings:**
```python
config = EmailConfig(
    smtp_server="smtp.mail.yahoo.com",
    smtp_port=587,
    username="your_email@yahoo.com",
    password="your_app_password",
    use_tls=True
)
```

### Custom SMTP Configuration

For other email providers:

```python
config = EmailConfig(
    smtp_server="your.smtp.server.com",
    smtp_port=587,  # or 465 for SSL, 25 for non-encrypted
    username="your_username",
    password="your_password",
    use_tls=True  # or False for SSL/non-encrypted
)
```

## 🔒 Security Configuration

### 1. Environment Variables

**Create `.env` file:**
```env
# Email Configuration
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
USE_TLS=true

# Optional: Logging configuration
LOG_LEVEL=INFO
LOG_FILE=email_sender.log
```

**Load in Python:**
```python
import os
from dotenv import load_dotenv  # pip install python-dotenv

# Load environment variables
load_dotenv()

config = EmailConfig(
    smtp_server=os.getenv("SMTP_SERVER"),
    smtp_port=int(os.getenv("SMTP_PORT", "587")),
    username=os.getenv("EMAIL_USERNAME"),
    password=os.getenv("EMAIL_PASSWORD"),
    use_tls=os.getenv("USE_TLS", "true").lower() == "true"
)
```

### 2. System Environment Variables

**Set system environment variables:**

**Windows:**
```cmd
setx EMAIL_USERNAME "your_email@gmail.com"
setx EMAIL_PASSWORD "your_app_password"
setx SMTP_SERVER "smtp.gmail.com"
setx SMTP_PORT "587"
```

**macOS/Linux:**
```bash
export EMAIL_USERNAME="your_email@gmail.com"
export EMAIL_PASSWORD="your_app_password"
export SMTP_SERVER="smtp.gmail.com"
export SMTP_PORT="587"

# Add to ~/.bashrc or ~/.zshrc for persistence
echo 'export EMAIL_USERNAME="your_email@gmail.com"' >> ~/.bashrc
```

### 3. Configuration File (config.ini)

**Create config.ini:**
```ini
[email]
smtp_server = smtp.gmail.com
smtp_port = 587
username = your_email@gmail.com
password = your_app_password
use_tls = true
```

**Load in Python:**
```python
import configparser

config_parser = configparser.ConfigParser()
config_parser.read('config.ini')

config = EmailConfig(
    smtp_server=config_parser.get('email', 'smtp_server'),
    smtp_port=config_parser.getint('email', 'smtp_port'),
    username=config_parser.get('email', 'username'),
    password=config_parser.get('email', 'password'),
    use_tls=config_parser.getboolean('email', 'use_tls')
)
```

## ⚙️ Advanced Configuration Options

### 1. Multiple Email Accounts

```python
# Define multiple configurations
gmail_config = EmailConfig(
    smtp_server="smtp.gmail.com",
    smtp_port=587,
    username="gmail_account@gmail.com",
    password="gmail_app_password",
    use_tls=True
)

outlook_config = EmailConfig(
    smtp_server="smtp-mail.outlook.com",
    smtp_port=587,
    username="outlook_account@outlook.com",
    password="outlook_password",
    use_tls=True
)

# Use different senders
gmail_sender = EmailSender(gmail_config)
outlook_sender = EmailSender(outlook_config)
```

### 2. Proxy Configuration (if needed)

```python
import smtplib
import socks

# Configure SOCKS proxy (if behind corporate firewall)
socks.set_default_proxy(socks.SOCKS5, "proxy_host", proxy_port)
socket.socket = socks.socksocket
```

### 3. SSL vs TLS Configuration

**TLS (Port 587) - Recommended:**
```python
config = EmailConfig(
    smtp_server="smtp.gmail.com",
    smtp_port=587,
    use_tls=True  # STARTTLS
)
```

**SSL (Port 465):**
```python
config = EmailConfig(
    smtp_server="smtp.gmail.com",
    smtp_port=465,
    use_tls=False  # Direct SSL connection
)
```

## 🧪 Testing Configuration

### 1. Test SMTP Connection

```python
from mail import EmailSender, EmailConfig

config = EmailConfig(
    smtp_server="smtp.gmail.com",
    smtp_port=587,
    username="your_email@gmail.com",
    password="your_app_password",
    use_tls=True
)

sender = EmailSender(config)

# Test connection (this will attempt to connect)
try:
    server = sender._create_smtp_connection()
    server.quit()
    print("✅ SMTP connection successful!")
except Exception as e:
    print(f"❌ SMTP connection failed: {e}")
```

### 2. Validate Configuration

```python
def validate_config(config):
    """Validate email configuration"""
    if not config.username:
        return False, "Username is required"
    if not config.password:
        return False, "Password is required"
    if not config.smtp_server:
        return False, "SMTP server is required"
    if not isinstance(config.smtp_port, int):
        return False, "SMTP port must be an integer"
    return True, "Configuration is valid"

# Test your configuration
is_valid, message = validate_config(config)
print(f"Configuration: {message}")
```

## 📝 Configuration Templates

### Complete .env Template

```env
# Email Configuration
EMAIL_USERNAME=your_email@provider.com
EMAIL_PASSWORD=your_app_password_here
SMTP_SERVER=smtp.provider.com
SMTP_PORT=587
USE_TLS=true

# Application Settings
TIME_INTERVAL=5
MAX_RETRIES=3
LOG_LEVEL=INFO
LOG_FILE=email_sender.log

# File Paths
RECIPIENTS_CSV=recipients.csv
ATTACHMENTS_DIR=attachments/
TEMPLATES_DIR=templates/

# Security
ENABLE_LOGGING=true
LOG_SENSITIVE_DATA=false
```

### Example Usage with Configuration

```python
import os
from mail import EmailSender, EmailConfig

def create_config_from_env():
    """Create configuration from environment variables"""
    return EmailConfig(
        smtp_server=os.getenv("SMTP_SERVER", "smtp.gmail.com"),
        smtp_port=int(os.getenv("SMTP_PORT", "587")),
        username=os.getenv("EMAIL_USERNAME"),
        password=os.getenv("EMAIL_PASSWORD"),
        use_tls=os.getenv("USE_TLS", "true").lower() == "true"
    )

# Use the configuration
config = create_config_from_env()
sender = EmailSender(config)
```

## ✅ Configuration Checklist

- [ ] Email provider account set up
- [ ] 2-Factor authentication enabled (Gmail/Yahoo)
- [ ] App password generated (Gmail/Yahoo)
- [ ] SMTP settings configured
- [ ] Credentials stored securely (environment variables)
- [ ] Configuration tested successfully
- [ ] .env file added to .gitignore

## 🔧 Next Steps

After configuration is complete:

1. **[Quick Start Tutorial](Quick-Start-Tutorial.md)** - Send your first email
2. **[Basic Usage](Basic-Usage.md)** - Learn core features
3. **[Security Best Practices](Security-Best-Practices.md)** - Secure your setup

---

**Need help with a specific provider?** Check our provider-specific guides:
- **[Gmail Setup](Gmail-Setup.md)**
- **[Outlook Setup](Outlook-Setup.md)**
- **[Yahoo Setup](Yahoo-Setup.md)**
