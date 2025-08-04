# Quick Start Tutorial

Get up and running with the Email Mailer Application in just 5 minutes! This tutorial will walk you through sending your first email.

## 🎯 What You'll Learn

- How to send a single email
- How to send bulk emails from a CSV file
- How to add file attachments
- How to use email templates

## 📋 Prerequisites

Before starting, make sure you have:
- ✅ Python 3.7+ installed
- ✅ The mailer application downloaded
- ✅ An email account (Gmail recommended for this tutorial)

## 🚀 Step 1: Basic Setup

### 1.1 Navigate to Project Directory

```bash
cd /path/to/mailer
```

### 1.2 Test the Installation

```bash
python test_mailer.py
```

You should see output confirming the application works correctly.

## 📧 Step 2: Send Your First Email

### 2.1 Create a Test Script

Create a file called `my_first_email.py`:

```python
from mail import EmailSender, EmailConfig, EmailData

# Configure your email settings
config = EmailConfig(
    smtp_server="smtp.gmail.com",
    smtp_port=587,
    username="your_email@gmail.com",        # 👈 Replace with your email
    password="your_app_password",           # 👈 Replace with your app password
    use_tls=True
)

# Create email sender
sender = EmailSender(config)

# Create email data
email_data = EmailData(
    to_email="recipient@example.com",       # 👈 Replace with recipient email
    to_name="Test Recipient",
    subject="My First Test Email",
    body="Hello! This is my first email sent using the Python mailer application."
)

# Send the email
success = sender.send_single_email(email_data)

if success:
    print("✅ Email sent successfully!")
else:
    print("❌ Failed to send email")
```

### 2.2 Update Your Credentials

**Important**: Replace the placeholder values:
- `your_email@gmail.com` - Your Gmail address
- `your_app_password` - Your Gmail App Password (see [Gmail Setup](Gmail-Setup.md))
- `recipient@example.com` - The email address you want to send to

### 2.3 Run Your First Email

```bash
python my_first_email.py
```

**Expected Output:**
```
2025-08-04 10:30:00 - INFO - Connected to SMTP server: smtp.gmail.com
2025-08-04 10:30:01 - INFO - Email sent successfully to: recipient@example.com
✅ Email sent successfully!
```

## 📋 Step 3: Send Bulk Emails from CSV

### 3.1 Prepare Your CSV File

Create or edit `recipients.csv`:

```csv
email,name,company
john.doe@example.com,John Doe,Tech Solutions
jane.smith@example.com,Jane Smith,Creative Agency
bob.johnson@example.com,Bob Johnson,Marketing Pro
```

### 3.2 Create Bulk Email Script

Create `bulk_email_test.py`:

```python
from mail import EmailSender, EmailConfig

# Same configuration as before
config = EmailConfig(
    smtp_server="smtp.gmail.com",
    smtp_port=587,
    username="your_email@gmail.com",        # 👈 Replace with your email
    password="your_app_password",           # 👈 Replace with your app password
    use_tls=True
)

sender = EmailSender(config)

# Email templates with placeholders
subject_template = "Hello {name}! Update from your friends"
body_template = """
Dear {name},

I hope this email finds you well at {company}!

This is a test email sent to demonstrate our bulk email functionality.

Best regards,
The Email Team

---
Sent to: {email}
"""

# Send bulk emails
results = sender.send_bulk_emails(
    recipients_csv="recipients.csv",
    subject_template=subject_template,
    body_template=body_template,
    time_interval=5  # 5 seconds between emails
)

print(f"✅ Successfully sent: {results['sent']}")
print(f"❌ Failed to send: {results['failed']}")
```

### 3.3 Run Bulk Email Test

```bash
python bulk_email_test.py
```

**Expected Output:**
```
2025-08-04 10:35:00 - INFO - Loaded 3 recipients from CSV
2025-08-04 10:35:00 - INFO - Starting bulk email send to 3 recipients
2025-08-04 10:35:01 - INFO - Email sent successfully to: john.doe@example.com
2025-08-04 10:35:01 - INFO - Progress: 1/3 emails sent
2025-08-04 10:35:01 - INFO - Waiting 5 seconds before next email...
2025-08-04 10:35:06 - INFO - Email sent successfully to: jane.smith@example.com
...
✅ Successfully sent: 3
❌ Failed to send: 0
```

## 📎 Step 4: Add File Attachments

### 4.1 Create Test Files

Create a simple text file for testing:

```bash
echo "This is a test attachment" > test_document.txt
echo "Another test file" > sample_file.txt
```

### 4.2 Email with Attachments Script

Create `email_with_attachments.py`:

```python
from mail import EmailSender, EmailConfig, EmailData

config = EmailConfig(
    smtp_server="smtp.gmail.com",
    smtp_port=587,
    username="your_email@gmail.com",        # 👈 Replace with your email
    password="your_app_password",           # 👈 Replace with your app password
    use_tls=True
)

sender = EmailSender(config)

# Email with attachments
email_data = EmailData(
    to_email="recipient@example.com",       # 👈 Replace with recipient
    subject="Email with Attachments Test",
    body="Please find the attached files.",
    attachments=[
        "test_document.txt",                # 👈 Make sure these files exist
        "sample_file.txt"
    ]
)

success = sender.send_single_email(email_data)

if success:
    print("✅ Email with attachments sent successfully!")
else:
    print("❌ Failed to send email with attachments")
```

### 4.3 Run Attachment Test

```bash
python email_with_attachments.py
```

## 🎨 Step 5: Advanced Templates

### 5.1 Create Advanced CSV

Update `recipients.csv` with more data:

```csv
email,name,company,position,location
john.doe@example.com,John Doe,Tech Solutions,Developer,New York
jane.smith@example.com,Jane Smith,Creative Agency,Designer,Los Angeles
bob.johnson@example.com,Bob Johnson,Marketing Pro,Manager,Chicago
```

### 5.2 Advanced Template Script

Create `advanced_templates.py`:

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

# Advanced email template
subject_template = "Greetings from {location}, {name}!"

body_template = """
Dear {name},

Hope you're doing great in your role as {position} at {company}!

We wanted to reach out from {location} to share some exciting news.

Key Details:
- Name: {name}
- Position: {position}
- Company: {company}
- Location: {location}
- Email: {email}

This demonstrates how our template system can personalize emails using CSV data.

Best regards,
The Template Team

P.S. This email was automatically personalized using your information from our CSV file.
"""

# Send personalized emails
results = sender.send_bulk_emails(
    recipients_csv="recipients.csv",
    subject_template=subject_template,
    body_template=body_template,
    time_interval=3  # 3 seconds between emails
)

print(f"📧 Personalized emails sent: {results['sent']}")
print(f"❌ Failed emails: {results['failed']}")
```

## ✅ Step 6: Verify Everything Works

### 6.1 Final Test Script

Create `complete_test.py`:

```python
from mail import EmailSender, EmailConfig, EmailData

def test_everything():
    """Test all features of the mailer application"""
    
    # Configuration
    config = EmailConfig(
        smtp_server="smtp.gmail.com",
        smtp_port=587,
        username="your_email@gmail.com",     # 👈 Replace
        password="your_app_password",        # 👈 Replace
        use_tls=True
    )
    
    sender = EmailSender(config)
    
    print("🧪 Testing Email Mailer Application...")
    
    # Test 1: CSV Loading
    recipients = sender.load_recipients_from_csv("recipients.csv")
    print(f"✅ CSV Test: Loaded {len(recipients)} recipients")
    
    # Test 2: Single Email (replace with your email for testing)
    test_email = EmailData(
        to_email="your_email@gmail.com",     # 👈 Send to yourself for testing
        subject="Test Email - Single Send",
        body="This is a test of single email functionality."
    )
    
    success = sender.send_single_email(test_email)
    print(f"✅ Single Email Test: {'Passed' if success else 'Failed'}")
    
    # Test 3: Template System
    template = "Hello {name} from {company}!"
    test_data = {"name": "Test User", "company": "Test Company"}
    formatted = template.format(**test_data)
    print(f"✅ Template Test: '{formatted}'")
    
    print("\n🎉 All tests completed!")
    print("📧 Check your email inbox for test messages")

if __name__ == "__main__":
    test_everything()
```

### 6.2 Run Complete Test

```bash
python complete_test.py
```

## 🎉 Congratulations!

You've successfully:
- ✅ Sent your first email
- ✅ Sent bulk emails from CSV
- ✅ Added file attachments
- ✅ Used advanced templates
- ✅ Tested all features

## 📚 Next Steps

Now that you're up and running, explore these guides:

1. **[Basic Usage](Basic-Usage.md)** - Learn all the features in detail
2. **[CSV Management](CSV-Management.md)** - Advanced CSV handling
3. **[File Attachments](File-Attachments.md)** - Working with attachments
4. **[Security Best Practices](Security-Best-Practices.md)** - Secure your setup

## 🔧 Customization Ideas

Try customizing the application:
- Add your company logo as an attachment
- Create different email templates for different purposes
- Set up different CSV files for different audiences
- Experiment with different time intervals

## 💡 Tips for Success

1. **Start Small**: Test with yourself first
2. **Use Test Data**: Don't send to real customers until you're confident
3. **Check Spam Folders**: Your test emails might end up there
4. **Monitor Logs**: Check `email_sender.log` for detailed information
5. **Backup Recipients**: Keep a backup of your CSV files

## ❓ Need Help?

If something doesn't work:
1. Check the **[Troubleshooting Guide](Troubleshooting.md)**
2. Verify your email credentials
3. Make sure files exist where expected
4. Check the log files for error details

---

**Ready for more?** Continue with the [Basic Usage Guide](Basic-Usage.md) to master all features!
