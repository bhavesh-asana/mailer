# API Reference

Complete technical documentation for the Email Mailer Application classes, methods, and functions.

## 📚 Core Classes

### EmailConfig

Configuration class for email server settings.

```python
@dataclass
class EmailConfig:
    smtp_server: str
    smtp_port: int
    username: str
    password: str
    use_tls: bool = True
```

**Parameters:**
- `smtp_server` (str): SMTP server hostname (e.g., "smtp.gmail.com")
- `smtp_port` (int): SMTP server port (typically 587 for TLS, 465 for SSL)
- `username` (str): Email account username/email address
- `password` (str): Email account password or app password
- `use_tls` (bool, optional): Whether to use TLS encryption. Defaults to True.

**Example:**
```python
config = EmailConfig(
    smtp_server="smtp.gmail.com",
    smtp_port=587,
    username="user@gmail.com",
    password="app_password",
    use_tls=True
)
```

---

### EmailData

Data structure for individual email information.

```python
@dataclass
class EmailData:
    to_email: str
    to_name: str = ""
    subject: str = ""
    body: str = ""
    attachments: List[str] = None
```

**Parameters:**
- `to_email` (str): Recipient email address
- `to_name` (str, optional): Recipient name for display
- `subject` (str, optional): Email subject line
- `body` (str, optional): Email body content
- `attachments` (List[str], optional): List of file paths to attach

**Example:**
```python
email_data = EmailData(
    to_email="recipient@example.com",
    to_name="John Doe",
    subject="Important Update",
    body="Hello John, this is an important message.",
    attachments=["document.pdf", "image.jpg"]
)
```

---

### EmailSender

Main class for sending emails with attachments and bulk functionality.

```python
class EmailSender:
    def __init__(self, config: EmailConfig)
```

**Parameters:**
- `config` (EmailConfig): Email configuration object

**Attributes:**
- `config` (EmailConfig): Email configuration
- `sent_count` (int): Number of successfully sent emails
- `failed_count` (int): Number of failed email attempts

## 🔧 EmailSender Methods

### send_single_email()

Send a single email with optional attachments.

```python
def send_single_email(self, email_data: EmailData) -> bool
```

**Parameters:**
- `email_data` (EmailData): Email data object containing recipient and content

**Returns:**
- `bool`: True if email sent successfully, False otherwise

**Example:**
```python
sender = EmailSender(config)
email_data = EmailData(
    to_email="user@example.com",
    subject="Test",
    body="Hello!"
)
success = sender.send_single_email(email_data)
```

**Raises:**
- `SMTPAuthenticationError`: Invalid credentials
- `SMTPRecipientsRefused`: Invalid recipient email
- `SMTPServerDisconnected`: Connection lost
- `FileNotFoundError`: Attachment file not found

---

### send_bulk_emails()

Send multiple emails from CSV data with time intervals.

```python
def send_bulk_emails(
    self,
    recipients_csv: str,
    subject_template: str,
    body_template: str,
    attachments: List[str] = None,
    time_interval: int = 5
) -> Dict[str, int]
```

**Parameters:**
- `recipients_csv` (str): Path to CSV file with recipient data
- `subject_template` (str): Email subject template with placeholders
- `body_template` (str): Email body template with placeholders
- `attachments` (List[str], optional): List of file paths to attach to all emails
- `time_interval` (int, optional): Seconds to wait between emails. Defaults to 5.

**Returns:**
- `Dict[str, int]`: Dictionary with 'sent' and 'failed' counts

**Template Placeholders:**
Use `{column_name}` syntax to insert CSV column values:
- `{name}` - Recipient name
- `{email}` - Recipient email
- `{company}` - Company name
- Any other CSV column

**Example:**
```python
results = sender.send_bulk_emails(
    recipients_csv="contacts.csv",
    subject_template="Hello {name}!",
    body_template="Dear {name}, greetings from {company}!",
    attachments=["brochure.pdf"],
    time_interval=10
)
print(f"Sent: {results['sent']}, Failed: {results['failed']}")
```

---

### load_recipients_from_csv()

Load recipient data from CSV file.

```python
@staticmethod
def load_recipients_from_csv(csv_file_path: str) -> List[Dict[str, str]]
```

**Parameters:**
- `csv_file_path` (str): Path to CSV file

**Returns:**
- `List[Dict[str, str]]`: List of dictionaries, each representing a recipient

**CSV Format Requirements:**
- Must have 'email' column
- Additional columns become template variables
- UTF-8 encoding recommended

**Example CSV:**
```csv
email,name,company,position
john@example.com,John Doe,Tech Corp,Developer
jane@example.com,Jane Smith,Design Co,Designer
```

**Example Usage:**
```python
recipients = EmailSender.load_recipients_from_csv("contacts.csv")
for recipient in recipients:
    print(f"{recipient['name']} at {recipient['company']}")
```

---

### create_sample_csv()

Create a sample CSV file for testing.

```python
@staticmethod
def create_sample_csv(file_path: str = "recipients.csv") -> None
```

**Parameters:**
- `file_path` (str, optional): Output file path. Defaults to "recipients.csv".

**Example:**
```python
EmailSender.create_sample_csv("test_recipients.csv")
```

**Generated CSV Structure:**
```csv
email,name,company
user1@example.com,John Doe,Tech Corp
user2@example.com,Jane Smith,Design Ltd
user3@example.com,Bob Johnson,Marketing Inc
```

## 🔒 Private Methods

### _create_smtp_connection()

Create and authenticate SMTP connection.

```python
def _create_smtp_connection(self) -> smtplib.SMTP
```

**Returns:**
- `smtplib.SMTP`: Authenticated SMTP connection object

**Raises:**
- `SMTPAuthenticationError`: Authentication failed
- `SMTPConnectError`: Cannot connect to server
- `SMTPServerDisconnected`: Connection lost

---

### _attach_files()

Attach files to email message.

```python
def _attach_files(self, msg: MIMEMultipart, file_paths: List[str]) -> None
```

**Parameters:**
- `msg` (MIMEMultipart): Email message object
- `file_paths` (List[str]): List of file paths to attach

**File Support:**
- Any file type (PDF, DOC, images, etc.)
- Automatic MIME type detection
- Base64 encoding for binary files

## 📊 Usage Examples

### Complete Example

```python
import os
from mail import EmailSender, EmailConfig, EmailData

# Configuration
config = EmailConfig(
    smtp_server=os.getenv("SMTP_SERVER", "smtp.gmail.com"),
    smtp_port=int(os.getenv("SMTP_PORT", "587")),
    username=os.getenv("EMAIL_USERNAME"),
    password=os.getenv("EMAIL_PASSWORD"),
    use_tls=True
)

# Initialize sender
sender = EmailSender(config)

# Single email
email_data = EmailData(
    to_email="recipient@example.com",
    subject="Test Email",
    body="Hello, this is a test!",
    attachments=["document.pdf"]
)

success = sender.send_single_email(email_data)

# Bulk emails
results = sender.send_bulk_emails(
    recipients_csv="contacts.csv",
    subject_template="Hello {name}!",
    body_template="Dear {name}, message from {company}.",
    time_interval=5
)

# Check results
print(f"Single email: {'✅' if success else '❌'}")
print(f"Bulk emails - Sent: {results['sent']}, Failed: {results['failed']}")
```

### Error Handling Example

```python
from mail import EmailSender, EmailConfig, EmailData
import smtplib

config = EmailConfig(
    smtp_server="smtp.gmail.com",
    smtp_port=587,
    username="user@gmail.com",
    password="password",
    use_tls=True
)

sender = EmailSender(config)

try:
    email_data = EmailData(
        to_email="test@example.com",
        subject="Test",
        body="Test message"
    )
    
    success = sender.send_single_email(email_data)
    
except smtplib.SMTPAuthenticationError:
    print("❌ Authentication failed - check credentials")
except smtplib.SMTPRecipientsRefused:
    print("❌ Recipient email address rejected")
except smtplib.SMTPServerDisconnected:
    print("❌ Connection to SMTP server lost")
except FileNotFoundError as e:
    print(f"❌ Attachment file not found: {e}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
```

### Bulk Email with Progress Tracking

```python
import time
from mail import EmailSender, EmailConfig

def send_with_progress(sender, csv_file, subject, body, interval=5):
    """Send bulk emails with custom progress tracking"""
    
    recipients = sender.load_recipients_from_csv(csv_file)
    total = len(recipients)
    
    print(f"📧 Starting bulk send to {total} recipients...")
    
    for i, recipient in enumerate(recipients, 1):
        try:
            email_data = EmailData(
                to_email=recipient['email'],
                subject=subject.format(**recipient),
                body=body.format(**recipient)
            )
            
            success = sender.send_single_email(email_data)
            status = "✅" if success else "❌"
            
            print(f"{status} [{i}/{total}] {recipient['email']}")
            
            if i < total:
                print(f"⏳ Waiting {interval} seconds...")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print(f"\n⚠️ Interrupted after {i-1}/{total} emails")
            break
        except Exception as e:
            print(f"❌ Error sending to {recipient['email']}: {e}")
    
    print(f"\n📊 Final Stats: {sender.sent_count} sent, {sender.failed_count} failed")

# Usage
config = EmailConfig(...)
sender = EmailSender(config)

send_with_progress(
    sender=sender,
    csv_file="recipients.csv",
    subject="Hello {name}!",
    body="Dear {name}, message content here.",
    interval=10
)
```

## 🚨 Exception Handling

### Common Exceptions

| Exception | Cause | Solution |
|-----------|-------|----------|
| `SMTPAuthenticationError` | Wrong username/password | Check credentials, use app password |
| `SMTPRecipientsRefused` | Invalid email address | Verify recipient email format |
| `SMTPServerDisconnected` | Network/server issue | Check internet, retry connection |
| `FileNotFoundError` | Missing attachment | Verify file paths exist |
| `UnicodeDecodeError` | CSV encoding issue | Save CSV as UTF-8 |
| `KeyError` | Missing CSV column | Check template placeholders match CSV headers |

### Best Practices

1. **Always use try-except blocks**
2. **Check file existence before attaching**
3. **Validate email addresses**
4. **Use environment variables for credentials**
5. **Test with small batches first**
6. **Monitor log files for issues**

## 📋 Return Values

### send_single_email()
- `True`: Email sent successfully
- `False`: Email failed to send

### send_bulk_emails()
```python
{
    "sent": 15,    # Number of successful sends
    "failed": 2    # Number of failed sends
}
```

### load_recipients_from_csv()
```python
[
    {"email": "user1@example.com", "name": "John", "company": "Corp"},
    {"email": "user2@example.com", "name": "Jane", "company": "Inc"}
]
```

---

**Need more help?** Check the [Code Examples](Code-Examples.md) page for practical implementations!
