# Security Best Practices

Essential security guidelines for the Email Mailer Application to protect your credentials and maintain secure email sending practices.

## 🔐 Credential Security

### 1. Never Store Credentials in Code

**❌ DON'T DO THIS:**
```python
# NEVER commit credentials to code!
config = EmailConfig(
    smtp_server="smtp.gmail.com",
    smtp_port=587,
    username="myemail@gmail.com",      # ❌ Exposed
    password="mypassword123",          # ❌ Exposed
    use_tls=True
)
```

**✅ DO THIS INSTEAD:**
```python
import os
from dotenv import load_dotenv

load_dotenv()  # Load from .env file

config = EmailConfig(
    smtp_server=os.getenv("SMTP_SERVER"),
    smtp_port=int(os.getenv("SMTP_PORT")),
    username=os.getenv("EMAIL_USERNAME"),
    password=os.getenv("EMAIL_PASSWORD"),
    use_tls=True
)
```

### 2. Use Environment Variables

**Create `.env` file:**
```env
# Email Configuration
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password_here
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# Keep this file in .gitignore!
```

**Load environment variables:**
```python
import os
from dotenv import load_dotenv

# Method 1: Using python-dotenv
load_dotenv()
username = os.getenv("EMAIL_USERNAME")
password = os.getenv("EMAIL_PASSWORD")

# Method 2: System environment variables
username = os.environ.get("EMAIL_USERNAME")
password = os.environ.get("EMAIL_PASSWORD")
```

### 3. System Environment Variables

**Windows:**
```cmd
# Set permanently
setx EMAIL_USERNAME "your_email@gmail.com"
setx EMAIL_PASSWORD "your_app_password"

# Set for current session
set EMAIL_USERNAME=your_email@gmail.com
set EMAIL_PASSWORD=your_app_password
```

**macOS/Linux:**
```bash
# Add to ~/.bashrc or ~/.zshrc for persistence
export EMAIL_USERNAME="your_email@gmail.com"
export EMAIL_PASSWORD="your_app_password"

# Or use for current session
EMAIL_USERNAME="your_email@gmail.com" python mail.py
```

## 🛡️ Email Provider Security

### Gmail Security Setup

1. **Enable 2-Factor Authentication**
   - Go to Google Account settings
   - Security → 2-Step Verification
   - **Never disable 2FA** for accounts with app passwords

2. **Use App Passwords (Required)**
   ```python
   # ❌ Never use regular password
   password="your_gmail_password"
   
   # ✅ Always use 16-character app password
   password="abcd efgh ijkl mnop"  # Generated app password
   ```

3. **Limit App Password Scope**
   - Create specific app passwords for different applications
   - Revoke unused app passwords regularly
   - Monitor app password usage in Google Account

4. **Account Security Monitoring**
   - Check "Recent security activity" regularly
   - Enable login alerts
   - Review connected apps quarterly

### Outlook Security Setup

1. **Use Regular Password** (no app password needed for personal accounts)
2. **Enable 2FA** on Microsoft account
3. **Monitor sign-in activity**
4. **Use least-privilege principle**

### Yahoo Security Setup

1. **Enable 2-Factor Authentication** (required for app passwords)
2. **Generate App Password** (like Gmail)
3. **Regular security checkups**

## 🗂️ File and Data Security

### 1. Protect Recipient Data

**CSV File Security:**
```python
# ❌ Don't commit real recipient data
real_recipients.csv       # Contains real email addresses
client_contacts.csv       # Customer data
production_data.csv       # Live data

# ✅ Use sample data for development
sample_recipients.csv     # Fake test data
test_contacts.csv         # Development data
demo_data.csv            # Example data
```

**Add to `.gitignore`:**
```gitignore
# Real recipient data
*_real.csv
*_production.csv
*_client.csv
*_customers.csv
contacts_*.csv
recipients_live.csv

# Email logs with sensitive data
email_sender.log
*.log
```

### 2. Secure File Permissions

**Linux/macOS:**
```bash
# Restrict access to credential files
chmod 600 .env                    # Only owner can read/write
chmod 600 config.ini             # Only owner can read/write
chmod 644 mail.py                # Read-only for group/others

# Check permissions
ls -la .env
# Should show: -rw-------
```

**Windows:**
```cmd
# Remove inheritance and set specific permissions
icacls .env /inheritance:r
icacls .env /grant:r "%USERNAME%:F"
```

### 3. Attachment Security

**Validate file types:**
```python
import os
from pathlib import Path

ALLOWED_EXTENSIONS = {'.pdf', '.txt', '.doc', '.docx', '.jpg', '.png'}

def validate_attachment(file_path):
    """Validate attachment before sending"""
    path = Path(file_path)
    
    # Check file exists
    if not path.exists():
        raise FileNotFoundError(f"Attachment not found: {file_path}")
    
    # Check file extension
    if path.suffix.lower() not in ALLOWED_EXTENSIONS:
        raise ValueError(f"File type not allowed: {path.suffix}")
    
    # Check file size (10MB limit)
    if path.stat().st_size > 10 * 1024 * 1024:
        raise ValueError(f"File too large: {path.name}")
    
    return True

# Use before attaching
for attachment in attachments:
    validate_attachment(attachment)
```

**Scan attachments:**
```python
import mimetypes

def scan_attachment(file_path):
    """Basic attachment security scan"""
    
    # Check MIME type
    mime_type, _ = mimetypes.guess_type(file_path)
    
    dangerous_types = [
        'application/x-executable',
        'application/x-msdos-program',
        'application/x-msdownload'
    ]
    
    if mime_type in dangerous_types:
        raise ValueError(f"Potentially dangerous file type: {mime_type}")
    
    return True
```

## 🔍 Logging Security

### 1. Secure Logging Configuration

```python
import logging
from pathlib import Path

def setup_secure_logging():
    """Setup logging without exposing sensitive data"""
    
    # Create logs directory with restricted permissions
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / 'email_sender.log'),
            logging.StreamHandler()
        ]
    )
    
    # Set restrictive permissions on log file
    log_file = log_dir / 'email_sender.log'
    if log_file.exists():
        log_file.chmod(0o600)  # Owner read/write only

setup_secure_logging()
```

### 2. Filter Sensitive Data from Logs

```python
import re

class SensitiveDataFilter(logging.Filter):
    """Filter to remove sensitive data from logs"""
    
    def filter(self, record):
        # Remove email addresses from log messages
        record.msg = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 
                           '[EMAIL_REDACTED]', str(record.msg))
        
        # Remove potential passwords
        record.msg = re.sub(r'password["\s]*[:=]["\s]*[^\s"]+', 
                           'password=[REDACTED]', str(record.msg))
        
        return True

# Add filter to logger
logger = logging.getLogger()
logger.addFilter(SensitiveDataFilter())
```

### 3. Log Rotation and Cleanup

```python
import logging.handlers
import os
from datetime import datetime, timedelta

def setup_log_rotation():
    """Setup log rotation with automatic cleanup"""
    
    # Rotating file handler (10MB max, keep 5 files)
    handler = logging.handlers.RotatingFileHandler(
        'email_sender.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    
    # Custom cleanup
    def cleanup_old_logs():
        """Remove logs older than 30 days"""
        cutoff = datetime.now() - timedelta(days=30)
        
        for file in os.listdir('.'):
            if file.startswith('email_sender.log'):
                file_time = datetime.fromtimestamp(os.path.getmtime(file))
                if file_time < cutoff:
                    os.remove(file)
    
    cleanup_old_logs()
```

## 🌐 Network Security

### 1. Secure SMTP Connections

**Always use encryption:**
```python
# ✅ Secure configurations
config_tls = EmailConfig(
    smtp_server="smtp.gmail.com",
    smtp_port=587,        # TLS port
    use_tls=True         # Enable TLS
)

config_ssl = EmailConfig(
    smtp_server="smtp.gmail.com",
    smtp_port=465,        # SSL port
    use_tls=False        # Direct SSL
)

# ❌ Never use unencrypted
config_insecure = EmailConfig(
    smtp_port=25,         # Unencrypted port
    use_tls=False        # No encryption
)
```

### 2. Certificate Validation

```python
import ssl
import smtplib

def create_secure_smtp_connection(server, port):
    """Create SMTP connection with certificate validation"""
    
    # Create secure SSL context
    context = ssl.create_default_context()
    
    # Require certificate verification
    context.check_hostname = True
    context.verify_mode = ssl.CERT_REQUIRED
    
    # Connect with security
    server = smtplib.SMTP(server, port)
    server.starttls(context=context)
    
    return server
```

### 3. Rate Limiting and Abuse Prevention

```python
import time
from datetime import datetime, timedelta

class RateLimiter:
    """Prevent email abuse with rate limiting"""
    
    def __init__(self, max_emails_per_hour=100):
        self.max_emails_per_hour = max_emails_per_hour
        self.sent_times = []
    
    def can_send_email(self):
        """Check if we can send another email"""
        now = datetime.now()
        hour_ago = now - timedelta(hours=1)
        
        # Remove old entries
        self.sent_times = [t for t in self.sent_times if t > hour_ago]
        
        # Check limit
        if len(self.sent_times) >= self.max_emails_per_hour:
            return False
        
        # Record this attempt
        self.sent_times.append(now)
        return True
    
    def wait_time_until_next_email(self):
        """Calculate wait time until next email can be sent"""
        if not self.sent_times:
            return 0
        
        oldest = min(self.sent_times)
        hour_from_oldest = oldest + timedelta(hours=1)
        wait_time = (hour_from_oldest - datetime.now()).total_seconds()
        
        return max(0, wait_time)

# Usage
rate_limiter = RateLimiter(max_emails_per_hour=50)

def send_with_rate_limiting(sender, email_data):
    """Send email with rate limiting"""
    if not rate_limiter.can_send_email():
        wait_time = rate_limiter.wait_time_until_next_email()
        print(f"Rate limit exceeded. Wait {wait_time:.0f} seconds.")
        return False
    
    return sender.send_single_email(email_data)
```

## 🔐 Configuration Security Template

**Create `secure_config.py`:**
```python
import os
import logging
from pathlib import Path
from mail import EmailConfig

class SecureEmailConfig:
    """Secure email configuration management"""
    
    def __init__(self):
        self.config = None
        self._validate_environment()
    
    def _validate_environment(self):
        """Validate that all required environment variables exist"""
        required_vars = [
            'EMAIL_USERNAME',
            'EMAIL_PASSWORD', 
            'SMTP_SERVER',
            'SMTP_PORT'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing environment variables: {missing_vars}")
    
    def get_config(self):
        """Get secure email configuration"""
        if not self.config:
            self.config = EmailConfig(
                smtp_server=os.getenv('SMTP_SERVER'),
                smtp_port=int(os.getenv('SMTP_PORT')),
                username=os.getenv('EMAIL_USERNAME'),
                password=os.getenv('EMAIL_PASSWORD'),
                use_tls=os.getenv('USE_TLS', 'true').lower() == 'true'
            )
        
        return self.config
    
    def validate_config(self):
        """Validate configuration security"""
        config = self.get_config()
        
        # Check for secure ports
        secure_ports = [587, 465]
        if config.smtp_port not in secure_ports:
            logging.warning(f"Using potentially insecure port: {config.smtp_port}")
        
        # Check TLS usage
        if not config.use_tls and config.smtp_port != 465:
            logging.warning("TLS not enabled - connection may be insecure")
        
        # Check password strength (basic)
        if len(config.password) < 8:
            logging.warning("Password appears to be weak")
        
        return True

# Usage
secure_config = SecureEmailConfig()
config = secure_config.get_config()
```

## ✅ Security Checklist

### Before Deployment:
- [ ] Environment variables configured
- [ ] Real credentials removed from code
- [ ] `.env` file in `.gitignore`
- [ ] App passwords generated (Gmail/Yahoo)
- [ ] 2FA enabled on email accounts
- [ ] File permissions set correctly
- [ ] Logging configured securely
- [ ] Rate limiting implemented
- [ ] TLS/SSL enabled

### Regular Maintenance:
- [ ] Review app passwords quarterly
- [ ] Rotate credentials annually
- [ ] Monitor email account activity
- [ ] Clean up old log files
- [ ] Update dependencies
- [ ] Review access permissions
- [ ] Check for security updates

### Incident Response:
- [ ] Document credential compromise procedure
- [ ] Know how to revoke app passwords
- [ ] Have backup authentication methods
- [ ] Monitor for unusual activity
- [ ] Know how to disable accounts quickly

## 🚨 Security Warnings

### ⚠️ Common Security Mistakes

1. **Committing credentials to Git**
2. **Using regular passwords instead of app passwords**
3. **Storing recipient data in public repositories**
4. **Logging sensitive information**
5. **Using unencrypted connections**
6. **Not setting file permissions**
7. **Sharing configuration files**
8. **Not rotating credentials**

### 🔍 Security Monitoring

Monitor these indicators:
- Unexpected authentication failures
- Unusual login locations in email accounts
- High bounce rates (could indicate compromised accounts)
- Unusual email sending patterns
- System access from unknown sources

---

**Remember**: Security is an ongoing process, not a one-time setup. Regularly review and update your security practices!
