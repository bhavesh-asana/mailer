# Email Sender with File Attachments and CSV Support

This project provides a comprehensive email sending solution with support for:
- Multiple email recipients from CSV files
- File attachments
- Configurable time intervals between emails
- Error handling and logging
- Template-based email content

## Features

- **Bulk Email Sending**: Send emails to multiple recipients from a CSV file
- **File Attachments**: Attach multiple files to emails
- **Time Intervals**: Configure delays between emails to avoid rate limiting
- **Template Support**: Use placeholders in subject and body for personalization
- **Logging**: Comprehensive logging of email sending progress and errors
- **Multiple SMTP Providers**: Support for Gmail, Outlook, Yahoo, and custom SMTP servers

## Quick Start

1. **Install dependencies** (optional):
   ```bash
   pip install -r requirements.txt
   ```

2. **Update email configuration** in `mail.py`:
   ```python
   config = EmailConfig(
       smtp_server="smtp.gmail.com",
       smtp_port=587,
       username="your_email@gmail.com",
       password="your_app_password",  # Use App Password for Gmail
       use_tls=True
   )
   ```

3. **Prepare your CSV file** with recipient data:
   ```csv
   email,name,company
   john@example.com,John Doe,Tech Corp
   jane@example.com,Jane Smith,Design Ltd
   ```

4. **Run the email sender**:
   ```bash
   python mail.py
   ```

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
