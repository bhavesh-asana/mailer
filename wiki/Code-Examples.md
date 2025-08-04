# Code Examples

Practical code examples for common use cases of the Email Mailer Application.

## 🚀 Basic Examples

### Single Email

```python
from mail import EmailSender, EmailConfig, EmailData

# Configuration
config = EmailConfig(
    smtp_server="smtp.gmail.com",
    smtp_port=587,
    username="your_email@gmail.com",
    password="your_app_password",
    use_tls=True
)

# Create sender
sender = EmailSender(config)

# Send single email
email_data = EmailData(
    to_email="recipient@example.com",
    subject="Hello from Python!",
    body="This is a test email sent using the mailer application."
)

success = sender.send_single_email(email_data)
print(f"Email sent: {'✅' if success else '❌'}")
```

### Bulk Emails from CSV

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

# Email templates
subject = "Hello {name}!"
body = """
Dear {name},

Thank you for being part of {company}!

Best regards,
The Team
"""

# Send bulk emails
results = sender.send_bulk_emails(
    recipients_csv="recipients.csv",
    subject_template=subject,
    body_template=body,
    time_interval=5
)

print(f"Sent: {results['sent']}, Failed: {results['failed']}")
```

## 📎 Attachment Examples

### Single File Attachment

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

# Email with single attachment
email_data = EmailData(
    to_email="recipient@example.com",
    subject="Document Attached",
    body="Please find the attached document.",
    attachments=["important_document.pdf"]
)

success = sender.send_single_email(email_data)
```

### Multiple File Attachments

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

# Email with multiple attachments
email_data = EmailData(
    to_email="recipient@example.com",
    subject="Multiple Files Attached",
    body="Please find the attached files.",
    attachments=[
        "document.pdf",
        "spreadsheet.xlsx",
        "presentation.pptx",
        "image.jpg"
    ]
)

success = sender.send_single_email(email_data)
```

### Bulk Emails with Attachments

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

# Same attachments for all recipients
results = sender.send_bulk_emails(
    recipients_csv="recipients.csv",
    subject_template="Monthly Report for {name}",
    body_template="Dear {name}, please find your monthly report attached.",
    attachments=["monthly_report.pdf", "summary.xlsx"],
    time_interval=10
)
```

## 🛡️ Secure Configuration Examples

### Environment Variables

```python
import os
from dotenv import load_dotenv
from mail import EmailSender, EmailConfig

# Load environment variables from .env file
load_dotenv()

def create_secure_config():
    """Create configuration from environment variables"""
    return EmailConfig(
        smtp_server=os.getenv("SMTP_SERVER"),
        smtp_port=int(os.getenv("SMTP_PORT")),
        username=os.getenv("EMAIL_USERNAME"),
        password=os.getenv("EMAIL_PASSWORD"),
        use_tls=os.getenv("USE_TLS", "true").lower() == "true"
    )

# Use secure configuration
config = create_secure_config()
sender = EmailSender(config)
```

### Configuration Validation

```python
import os
from mail import EmailSender, EmailConfig

def validate_and_create_config():
    """Validate environment variables and create config"""
    
    required_vars = {
        'SMTP_SERVER': 'SMTP server hostname',
        'SMTP_PORT': 'SMTP server port',
        'EMAIL_USERNAME': 'Email username',
        'EMAIL_PASSWORD': 'Email password'
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        if not os.getenv(var):
            missing_vars.append(f"{var} ({description})")
    
    if missing_vars:
        raise ValueError(f"Missing environment variables: {', '.join(missing_vars)}")
    
    return EmailConfig(
        smtp_server=os.getenv("SMTP_SERVER"),
        smtp_port=int(os.getenv("SMTP_PORT")),
        username=os.getenv("EMAIL_USERNAME"),
        password=os.getenv("EMAIL_PASSWORD"),
        use_tls=True
    )

# Usage
try:
    config = validate_and_create_config()
    sender = EmailSender(config)
    print("✅ Configuration validated successfully")
except ValueError as e:
    print(f"❌ Configuration error: {e}")
```

## 📊 CSV Processing Examples

### Advanced CSV Validation

```python
import csv
import re
from pathlib import Path
from mail import EmailSender

def validate_csv_file(csv_file_path):
    """Comprehensive CSV validation"""
    
    path = Path(csv_file_path)
    
    # Check file exists
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_file_path}")
    
    # Check file size
    if path.stat().st_size == 0:
        raise ValueError("CSV file is empty")
    
    recipients = []
    errors = []
    
    try:
        with open(path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            # Validate headers
            if 'email' not in reader.fieldnames:
                raise ValueError("CSV must have 'email' column")
            
            # Validate each row
            for row_num, row in enumerate(reader, 2):  # Start at 2 (header is row 1)
                email = row.get('email', '').strip()
                
                if not email:
                    errors.append(f"Row {row_num}: Missing email address")
                    continue
                
                # Basic email validation
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if not re.match(email_pattern, email):
                    errors.append(f"Row {row_num}: Invalid email format: {email}")
                    continue
                
                recipients.append(row)
    
    except UnicodeDecodeError:
        raise ValueError("CSV file encoding error. Please save as UTF-8.")
    except csv.Error as e:
        raise ValueError(f"CSV parsing error: {e}")
    
    if errors:
        raise ValueError(f"CSV validation errors:\n" + "\n".join(errors))
    
    return recipients

# Usage
try:
    recipients = validate_csv_file("recipients.csv")
    print(f"✅ CSV validated: {len(recipients)} valid recipients")
except ValueError as e:
    print(f"❌ CSV validation failed: {e}")
```

### Dynamic CSV Processing

```python
import pandas as pd
from mail import EmailSender, EmailConfig

def process_dynamic_csv(csv_file, email_config):
    """Process CSV with dynamic column mapping"""
    
    # Read CSV with pandas for advanced processing
    df = pd.read_csv(csv_file)
    
    # Clean and validate data
    df['email'] = df['email'].str.strip().str.lower()
    df = df.dropna(subset=['email'])  # Remove rows with missing emails
    df = df.drop_duplicates(subset=['email'])  # Remove duplicate emails
    
    # Create sender
    sender = EmailSender(email_config)
    
    # Dynamic template based on available columns
    available_columns = df.columns.tolist()
    
    if 'name' in available_columns:
        subject_template = "Hello {name}!"
        greeting = "Dear {name},"
    else:
        subject_template = "Hello!"
        greeting = "Dear Valued Customer,"
    
    if 'company' in available_columns:
        company_line = "We hope things are going well at {company}."
    else:
        company_line = "We hope you're doing well."
    
    body_template = f"""
{greeting}

{company_line}

This is an automated message from our system.

Best regards,
The Team

---
Email: {{email}}
"""
    
    # Convert back to list of dictionaries
    recipients = df.to_dict('records')
    
    # Send emails
    results = sender.send_bulk_emails(
        recipients_csv=csv_file,  # Still pass file for logging
        subject_template=subject_template,
        body_template=body_template,
        time_interval=5
    )
    
    return results

# Usage
config = EmailConfig(...)
results = process_dynamic_csv("contacts.csv", config)
```

## 🎨 Template Examples

### HTML Email Templates

```python
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from mail import EmailSender, EmailConfig

def send_html_email(sender, to_email, subject, html_content, text_content=None):
    """Send HTML email with fallback text content"""
    
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = sender.config.username
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Add text version (fallback)
        if text_content:
            msg.attach(MIMEText(text_content, 'plain'))
        
        # Add HTML version
        msg.attach(MIMEText(html_content, 'html'))
        
        # Send using existing SMTP connection method
        server = sender._create_smtp_connection()
        text = msg.as_string()
        server.sendmail(sender.config.username, to_email, text)
        server.quit()
        
        sender.sent_count += 1
        return True
        
    except Exception as e:
        sender.failed_count += 1
        print(f"Failed to send HTML email: {e}")
        return False

# Usage
config = EmailConfig(...)
sender = EmailSender(config)

html_template = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; }
        .header { background-color: #4CAF50; color: white; padding: 20px; }
        .content { padding: 20px; }
        .footer { background-color: #f1f1f1; padding: 10px; text-align: center; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Welcome {name}!</h1>
    </div>
    <div class="content">
        <p>Dear {name},</p>
        <p>Thank you for joining {company}!</p>
        <p>We're excited to have you on board.</p>
    </div>
    <div class="footer">
        <p>© 2025 Your Company. All rights reserved.</p>
    </div>
</body>
</html>
"""

text_template = """
Welcome {name}!

Dear {name},

Thank you for joining {company}!

We're excited to have you on board.

© 2025 Your Company. All rights reserved.
"""

# Send HTML email
recipients = [
    {"name": "John Doe", "email": "john@example.com", "company": "Tech Corp"},
    {"name": "Jane Smith", "email": "jane@example.com", "company": "Design Inc"}
]

for recipient in recipients:
    html_content = html_template.format(**recipient)
    text_content = text_template.format(**recipient)
    
    success = send_html_email(
        sender=sender,
        to_email=recipient['email'],
        subject=f"Welcome to our company, {recipient['name']}!",
        html_content=html_content,
        text_content=text_content
    )
```

### Conditional Templates

```python
from mail import EmailSender, EmailConfig

def create_conditional_template(recipient_data):
    """Create email template based on recipient data"""
    
    name = recipient_data.get('name', 'Valued Customer')
    company = recipient_data.get('company', '')
    position = recipient_data.get('position', '')
    industry = recipient_data.get('industry', '')
    
    # Conditional subject
    if position and 'manager' in position.lower():
        subject = f"Exclusive Manager Offer for {name}"
    elif company:
        subject = f"Special Offer for {company} - {name}"
    else:
        subject = f"Special Offer for {name}"
    
    # Conditional content
    greeting = f"Dear {name},"
    
    if position:
        role_line = f"As a {position}"
        if company:
            role_line += f" at {company}"
        role_line += ", we have a special offer for you."
    else:
        role_line = "We have a special offer for you."
    
    if industry:
        industry_line = f"Given your experience in {industry}, this opportunity is particularly relevant."
    else:
        industry_line = "This opportunity could be perfect for you."
    
    body = f"""
{greeting}

{role_line}

{industry_line}

Best regards,
The Sales Team

---
This email was sent to: {recipient_data['email']}
"""
    
    return subject, body

# Usage with bulk emails
def send_conditional_bulk_emails(sender, csv_file):
    """Send bulk emails with conditional templates"""
    
    recipients = sender.load_recipients_from_csv(csv_file)
    
    for recipient in recipients:
        subject, body = create_conditional_template(recipient)
        
        email_data = EmailData(
            to_email=recipient['email'],
            subject=subject,
            body=body
        )
        
        success = sender.send_single_email(email_data)
        print(f"{'✅' if success else '❌'} {recipient['email']}")
        
        time.sleep(5)  # Wait between emails

config = EmailConfig(...)
sender = EmailSender(config)
send_conditional_bulk_emails(sender, "recipients.csv")
```

## 🔄 Advanced Processing Examples

### Batch Processing with Error Recovery

```python
import time
import json
from datetime import datetime
from mail import EmailSender, EmailConfig, EmailData

class BatchEmailProcessor:
    """Advanced batch email processor with error recovery"""
    
    def __init__(self, config, batch_size=50, retry_attempts=3):
        self.sender = EmailSender(config)
        self.batch_size = batch_size
        self.retry_attempts = retry_attempts
        self.processed_emails = []
        self.failed_emails = []
        
    def save_progress(self, filename="email_progress.json"):
        """Save processing progress"""
        progress = {
            'timestamp': datetime.now().isoformat(),
            'processed': self.processed_emails,
            'failed': self.failed_emails,
            'stats': {
                'total_processed': len(self.processed_emails),
                'total_failed': len(self.failed_emails),
                'success_rate': len(self.processed_emails) / (len(self.processed_emails) + len(self.failed_emails)) if (len(self.processed_emails) + len(self.failed_emails)) > 0 else 0
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(progress, f, indent=2)
    
    def load_progress(self, filename="email_progress.json"):
        """Load previous processing progress"""
        try:
            with open(filename, 'r') as f:
                progress = json.load(f)
                self.processed_emails = progress.get('processed', [])
                self.failed_emails = progress.get('failed', [])
                return True
        except FileNotFoundError:
            return False
    
    def process_batch(self, recipients, subject_template, body_template, attachments=None):
        """Process a batch of recipients with error recovery"""
        
        for recipient in recipients:
            email = recipient['email']
            
            # Skip if already processed
            if email in self.processed_emails:
                print(f"⏭️  Skipping already processed: {email}")
                continue
            
            # Retry logic
            for attempt in range(self.retry_attempts):
                try:
                    subject = subject_template.format(**recipient)
                    body = body_template.format(**recipient)
                    
                    email_data = EmailData(
                        to_email=email,
                        subject=subject,
                        body=body,
                        attachments=attachments
                    )
                    
                    success = self.sender.send_single_email(email_data)
                    
                    if success:
                        self.processed_emails.append(email)
                        print(f"✅ [{len(self.processed_emails)}] Sent to: {email}")
                        break
                    else:
                        if attempt == self.retry_attempts - 1:
                            self.failed_emails.append(email)
                            print(f"❌ Failed after {self.retry_attempts} attempts: {email}")
                        else:
                            print(f"🔄 Retry {attempt + 1} for: {email}")
                            time.sleep(2)  # Short delay before retry
                
                except Exception as e:
                    print(f"❌ Error sending to {email}: {e}")
                    if attempt == self.retry_attempts - 1:
                        self.failed_emails.append(email)
                    else:
                        time.sleep(2)
            
            # Save progress periodically
            if len(self.processed_emails) % 10 == 0:
                self.save_progress()
            
            time.sleep(3)  # Delay between emails
    
    def process_csv_in_batches(self, csv_file, subject_template, body_template, attachments=None):
        """Process entire CSV file in batches"""
        
        # Load previous progress
        self.load_progress()
        
        recipients = self.sender.load_recipients_from_csv(csv_file)
        total_recipients = len(recipients)
        
        print(f"📧 Processing {total_recipients} recipients in batches of {self.batch_size}")
        
        # Process in batches
        for i in range(0, total_recipients, self.batch_size):
            batch = recipients[i:i + self.batch_size]
            batch_num = (i // self.batch_size) + 1
            total_batches = (total_recipients + self.batch_size - 1) // self.batch_size
            
            print(f"\n📦 Processing batch {batch_num}/{total_batches} ({len(batch)} recipients)")
            
            self.process_batch(batch, subject_template, body_template, attachments)
            
            # Save progress after each batch
            self.save_progress()
            
            # Longer delay between batches
            if i + self.batch_size < total_recipients:
                print(f"⏳ Waiting 30 seconds before next batch...")
                time.sleep(30)
        
        # Final report
        self.print_final_report()
    
    def print_final_report(self):
        """Print final processing report"""
        total = len(self.processed_emails) + len(self.failed_emails)
        success_rate = (len(self.processed_emails) / total * 100) if total > 0 else 0
        
        print(f"\n📊 Final Report:")
        print(f"✅ Successfully sent: {len(self.processed_emails)}")
        print(f"❌ Failed to send: {len(self.failed_emails)}")
        print(f"📈 Success rate: {success_rate:.1f}%")
        
        if self.failed_emails:
            print(f"\n❌ Failed emails:")
            for email in self.failed_emails:
                print(f"   - {email}")

# Usage
config = EmailConfig(...)
processor = BatchEmailProcessor(config, batch_size=25, retry_attempts=3)

processor.process_csv_in_batches(
    csv_file="large_recipient_list.csv",
    subject_template="Important Update for {name}",
    body_template="""
Dear {name},

We have an important update for {company}.

Best regards,
The Team
""",
    attachments=["update_document.pdf"]
)
```

### Progress Tracking Example

```python
import time
from datetime import datetime
from mail import EmailSender, EmailConfig

def send_with_progress_bar(sender, csv_file, subject_template, body_template, time_interval=5):
    """Send emails with visual progress tracking"""
    
    recipients = sender.load_recipients_from_csv(csv_file)
    total = len(recipients)
    
    print(f"📧 Sending emails to {total} recipients...")
    print(f"⏱️  Time interval: {time_interval} seconds")
    print(f"🕐 Estimated time: {(total * time_interval) / 60:.1f} minutes")
    print("-" * 50)
    
    start_time = datetime.now()
    
    for i, recipient in enumerate(recipients, 1):
        # Create progress bar
        progress = i / total
        bar_length = 30
        filled_length = int(bar_length * progress)
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        
        # Send email
        email_data = EmailData(
            to_email=recipient['email'],
            subject=subject_template.format(**recipient),
            body=body_template.format(**recipient)
        )
        
        success = sender.send_single_email(email_data)
        status = "✅" if success else "❌"
        
        # Calculate ETA
        elapsed = datetime.now() - start_time
        if i > 1:
            avg_time_per_email = elapsed.total_seconds() / (i - 1)
            remaining_emails = total - i
            eta_seconds = remaining_emails * avg_time_per_email
            eta_minutes = eta_seconds / 60
            eta_str = f"ETA: {eta_minutes:.1f}m"
        else:
            eta_str = "ETA: calculating..."
        
        # Print progress
        print(f"\r{status} [{bar}] {i}/{total} ({progress:.1%}) - {eta_str}", end="")
        
        # Wait between emails (except for last one)
        if i < total:
            time.sleep(time_interval)
    
    # Final summary
    total_time = datetime.now() - start_time
    print(f"\n\n📊 Completed in {total_time.total_seconds() / 60:.1f} minutes")
    print(f"✅ Sent: {sender.sent_count}")
    print(f"❌ Failed: {sender.failed_count}")

# Usage
config = EmailConfig(...)
sender = EmailSender(config)

send_with_progress_bar(
    sender=sender,
    csv_file="recipients.csv",
    subject_template="Hello {name}!",
    body_template="Dear {name}, this is a test email.",
    time_interval=3
)
```

---

**More Examples**: Check the [API Reference](API-Reference.md) for complete method documentation and the [Quick Start Tutorial](Quick-Start-Tutorial.md) for step-by-step examples!
