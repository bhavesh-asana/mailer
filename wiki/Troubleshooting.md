# Troubleshooting Guide

Common issues and solutions for the Email Mailer Application.

## 🚨 Authentication Issues

### Gmail Authentication Error

**Error Message:**
```
SMTPAuthenticationError: (535, '5.7.8 Username and Password not accepted')
```

**Solutions:**

1. **Enable 2-Factor Authentication and use App Password**
   ```bash
   # Check if you're using regular password instead of app password
   # Solution: Generate Gmail App Password
   ```
   - Go to [Gmail Setup Guide](Gmail-Setup.md)
   - Enable 2FA on your Google account
   - Generate an App Password
   - Use the 16-character app password, not your regular password

2. **Check credentials format**
   ```python
   # Wrong ❌
   config = EmailConfig(
       username="myemail",  # Missing @gmail.com
       password="my regular password"  # Should be app password
   )
   
   # Correct ✅
   config = EmailConfig(
       username="myemail@gmail.com",  # Full email address
       password="abcd efgh ijkl mnop"  # 16-character app password
   )
   ```

3. **Less Secure Apps (Deprecated)**
   - Don't use "Less secure app access" - it's deprecated
   - Always use App Passwords instead

### Outlook Authentication Issues

**Error Message:**
```
SMTPAuthenticationError: (535, '5.7.139 Authentication unsuccessful')
```

**Solutions:**

1. **Use correct SMTP settings**
   ```python
   config = EmailConfig(
       smtp_server="smtp-mail.outlook.com",  # Not smtp.outlook.com
       smtp_port=587,
       username="your_email@outlook.com",
       password="your_regular_password",  # No app password needed
       use_tls=True
   )
   ```

2. **Check account type**
   - Personal Outlook accounts: Use regular password
   - Work/School accounts: May need app password or OAuth

### Yahoo Authentication Issues

**Solutions:**

1. **Generate App Password**
   - Yahoo requires app passwords like Gmail
   - Enable 2FA first
   - Generate app password in account settings

2. **Use correct settings**
   ```python
   config = EmailConfig(
       smtp_server="smtp.mail.yahoo.com",
       smtp_port=587,
       username="your_email@yahoo.com",
       password="your_app_password",  # Not regular password
       use_tls=True
   )
   ```

## 🌐 Connection Issues

### SMTP Connection Timeout

**Error Message:**
```
SMTPConnectError: (10060, 'Connection attempt failed')
```

**Solutions:**

1. **Check firewall/antivirus**
   ```bash
   # Temporarily disable firewall to test
   # Add Python to firewall exceptions
   ```

2. **Try different ports**
   ```python
   # Try SSL instead of TLS
   config = EmailConfig(
       smtp_server="smtp.gmail.com",
       smtp_port=465,  # SSL port instead of 587
       use_tls=False   # Use direct SSL
   )
   ```

3. **Check corporate network**
   ```bash
   # Test from personal network
   # Contact IT about SMTP blocking
   ```

### Server Not Found

**Error Message:**
```
gaierror: [Errno 11001] getaddrinfo failed
```

**Solutions:**

1. **Check SMTP server spelling**
   ```python
   # Wrong ❌
   smtp_server="smtp.gamil.com"  # Typo
   
   # Correct ✅
   smtp_server="smtp.gmail.com"
   ```

2. **Check internet connection**
   ```bash
   # Test connectivity
   ping smtp.gmail.com
   ```

## 📁 File and Path Issues

### Attachment File Not Found

**Error Message:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'document.pdf'
```

**Solutions:**

1. **Use absolute paths**
   ```python
   import os
   
   # Wrong ❌
   attachments=["document.pdf"]
   
   # Correct ✅
   attachments=[os.path.abspath("document.pdf")]
   # or
   attachments=["/full/path/to/document.pdf"]
   ```

2. **Check file existence**
   ```python
   import os
   
   def validate_attachments(file_paths):
       for path in file_paths:
           if not os.path.exists(path):
               print(f"❌ File not found: {path}")
               return False
       return True
   
   # Use before sending
   if validate_attachments(["document.pdf"]):
       # Send email
   ```

3. **Check file permissions**
   ```bash
   # Linux/macOS
   chmod 644 document.pdf
   
   # Windows - check file properties
   ```

### CSV File Issues

**Error Message:**
```
FileNotFoundError: CSV file not found: recipients.csv
```

**Solutions:**

1. **Check CSV file location**
   ```python
   import os
   
   csv_path = "recipients.csv"
   if os.path.exists(csv_path):
       print("✅ CSV file found")
   else:
       print(f"❌ CSV file not found at: {os.path.abspath(csv_path)}")
   ```

2. **Create sample CSV**
   ```python
   from mail import EmailSender
   
   # Create sample file
   EmailSender.create_sample_csv("test_recipients.csv")
   ```

3. **Check CSV format**
   ```csv
   # Wrong ❌ - Missing email column
   name,company
   John,Tech Corp
   
   # Correct ✅ - Has email column
   email,name,company
   john@example.com,John,Tech Corp
   ```

## 📊 CSV and Template Issues

### Template KeyError

**Error Message:**
```
KeyError: 'name'
```

**Solutions:**

1. **Check CSV headers match template**
   ```python
   # CSV headers: email,full_name,company_name
   # Template uses: {name} ❌
   # Should use: {full_name} ✅
   
   subject_template = "Hello {full_name} from {company_name}!"
   ```

2. **Add default values**
   ```python
   # Safe template formatting
   def safe_format(template, data):
       try:
           return template.format(**data)
       except KeyError as e:
           print(f"Missing template field: {e}")
           # Provide defaults
           data.setdefault('name', 'Friend')
           return template.format(**data)
   ```

3. **Validate CSV structure**
   ```python
   def validate_csv_for_template(csv_file, template):
       import re
       recipients = EmailSender.load_recipients_from_csv(csv_file)
       
       # Extract template variables
       template_vars = re.findall(r'\{(\w+)\}', template)
       
       if recipients:
           csv_columns = recipients[0].keys()
           missing = set(template_vars) - set(csv_columns)
           if missing:
               print(f"❌ Missing CSV columns: {missing}")
               return False
       return True
   ```

### CSV Encoding Issues

**Error Message:**
```
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff
```

**Solutions:**

1. **Save CSV as UTF-8**
   - Excel: Save As → CSV UTF-8
   - Google Sheets: Download as CSV
   - Text editor: Save with UTF-8 encoding

2. **Handle encoding in code**
   ```python
   import csv
   
   def load_csv_with_encoding(file_path):
       encodings = ['utf-8', 'latin-1', 'cp1252']
       
       for encoding in encodings:
           try:
               with open(file_path, 'r', encoding=encoding) as file:
                   return list(csv.DictReader(file))
           except UnicodeDecodeError:
               continue
       
       raise ValueError("Could not decode CSV file")
   ```

## 🐌 Performance Issues

### Slow Email Sending

**Issue:** Emails taking too long to send

**Solutions:**

1. **Reduce time intervals**
   ```python
   # Faster sending (but check rate limits)
   results = sender.send_bulk_emails(
       time_interval=1  # 1 second instead of 5
   )
   ```

2. **Check email provider limits**
   ```python
   # Gmail: 500 emails/day for free accounts
   # Outlook: 300 emails/day
   # Consider batch processing
   
   def send_in_batches(recipients, batch_size=50):
       for i in range(0, len(recipients), batch_size):
           batch = recipients[i:i + batch_size]
           # Send batch
           # Wait longer between batches
   ```

3. **Optimize attachments**
   ```python
   # Compress large files
   # Limit attachment sizes
   # Consider cloud links instead of attachments
   ```

### Memory Issues with Large CSV

**Issue:** Application crashes with large recipient lists

**Solutions:**

1. **Process in chunks**
   ```python
   def process_large_csv(csv_file, chunk_size=100):
       import pandas as pd
       
       for chunk in pd.read_csv(csv_file, chunksize=chunk_size):
           # Process each chunk
           chunk.to_csv('temp_chunk.csv', index=False)
           # Send emails for this chunk
   ```

2. **Use generators**
   ```python
   def csv_generator(file_path):
       with open(file_path, 'r') as file:
           reader = csv.DictReader(file)
           for row in reader:
               yield row
   
   # Use generator instead of loading all at once
   for recipient in csv_generator('large_file.csv'):
       # Process one at a time
   ```

## 📝 Logging and Debugging

### Enable Debug Logging

```python
import logging

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler()
    ]
)

# This will show detailed SMTP communication
```

### Check Log Files

```bash
# View recent log entries
tail -f email_sender.log

# Search for errors
grep -i error email_sender.log

# Count successful sends
grep -c "Email sent successfully" email_sender.log
```

### Test SMTP Connection Manually

```python
import smtplib

def test_smtp_connection(server, port, username, password):
    try:
        server = smtplib.SMTP(server, port)
        server.starttls()
        server.login(username, password)
        server.quit()
        print("✅ SMTP connection successful")
        return True
    except Exception as e:
        print(f"❌ SMTP connection failed: {e}")
        return False

# Test your settings
test_smtp_connection(
    "smtp.gmail.com", 
    587, 
    "your_email@gmail.com", 
    "your_app_password"
)
```

## 🔧 Environment Issues

### Python Version Issues

**Issue:** Application doesn't work with older Python

**Solutions:**

1. **Check Python version**
   ```bash
   python --version
   # Need Python 3.7+
   ```

2. **Install newer Python**
   ```bash
   # Windows: Download from python.org
   # macOS: brew install python3
   # Linux: sudo apt install python3.9
   ```

3. **Use specific Python version**
   ```bash
   python3.9 mail.py
   # or
   /usr/bin/python3.9 mail.py
   ```

### Module Import Issues

**Error Message:**
```
ModuleNotFoundError: No module named 'mail'
```

**Solutions:**

1. **Check working directory**
   ```bash
   ls  # Should show mail.py
   pwd  # Check current directory
   ```

2. **Use full path**
   ```bash
   cd /full/path/to/mailer
   python mail.py
   ```

3. **Check Python path**
   ```python
   import sys
   print(sys.path)
   # Add current directory if needed
   sys.path.append('.')
   ```

## 📋 Quick Diagnostic Script

Create `diagnose.py` to check common issues:

```python
#!/usr/bin/env python3
"""Diagnostic script for Email Mailer Application"""

import os
import sys
import csv
import smtplib
from pathlib import Path

def diagnose_system():
    """Run system diagnostics"""
    print("🔍 Email Mailer Diagnostics")
    print("=" * 40)
    
    # Check Python version
    py_version = sys.version_info
    print(f"Python Version: {py_version.major}.{py_version.minor}.{py_version.micro}")
    if py_version < (3, 7):
        print("❌ Python 3.7+ required")
    else:
        print("✅ Python version OK")
    
    # Check files
    required_files = ['mail.py', 'recipients.csv']
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} found")
        else:
            print(f"❌ {file} missing")
    
    # Check CSV format
    if os.path.exists('recipients.csv'):
        try:
            with open('recipients.csv', 'r') as f:
                reader = csv.DictReader(f)
                headers = reader.fieldnames
                if 'email' in headers:
                    print("✅ CSV has email column")
                else:
                    print("❌ CSV missing email column")
        except Exception as e:
            print(f"❌ CSV error: {e}")
    
    # Test SMTP connection (if credentials provided)
    print("\n📧 To test SMTP connection, run:")
    print("python -c \"from mail import EmailConfig; print('Import successful')\"")

if __name__ == "__main__":
    diagnose_system()
```

Run diagnostics:
```bash
python diagnose.py
```

## 📞 Getting Help

### Information to Collect

When asking for help, include:

1. **Error message** (full traceback)
2. **Python version** (`python --version`)
3. **Operating system** (Windows/macOS/Linux)
4. **Email provider** (Gmail/Outlook/Yahoo)
5. **Code snippet** that's failing
6. **Log file** contents (if available)

### Useful Debug Commands

```bash
# Check Python modules
python -c "import smtplib, email, csv; print('All modules available')"

# Check file permissions
ls -la *.csv *.py

# Test network connectivity
ping smtp.gmail.com

# Check environment variables
env | grep EMAIL
```

## ✅ Prevention Tips

1. **Always test with yourself first**
2. **Use environment variables for credentials**
3. **Start with small CSV files**
4. **Keep backups of working configurations**
5. **Monitor log files regularly**
6. **Test after any changes**

---

**Still stuck?** Check the [FAQ](FAQ.md) or create an issue with your diagnostic information!
