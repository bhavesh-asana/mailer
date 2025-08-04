# Frequently Asked Questions (FAQ)

Common questions and answers about the Email Mailer Application.

## 🚀 Getting Started

### Q: What email providers are supported?
**A:** The application supports any SMTP-enabled email provider, including:
- **Gmail** (requires App Password)
- **Outlook/Hotmail** (uses regular password)
- **Yahoo Mail** (requires App Password)
- **Custom SMTP servers** (corporate email, etc.)

### Q: Do I need to install additional packages?
**A:** No! The core functionality uses only Python built-in modules. Optional packages like `python-dotenv` and `pandas` can enhance the experience but aren't required.

### Q: What Python version do I need?
**A:** Python 3.7 or higher. The application has been tested on Python 3.7, 3.8, 3.9, 3.10, and 3.11.

## 🔐 Authentication & Security

### Q: Why am I getting authentication errors with Gmail?
**A:** Gmail requires App Passwords instead of your regular password:
1. Enable 2-Factor Authentication on your Google account
2. Generate an App Password (16 characters)
3. Use the App Password in your configuration
4. See the [Gmail Setup Guide](Gmail-Setup.md) for detailed instructions

### Q: Do I need an App Password for Outlook?
**A:** No, Outlook/Hotmail personal accounts can use your regular password. However, work/school accounts may require different authentication methods.

### Q: How do I keep my credentials secure?
**A:** Use environment variables or `.env` files:
```bash
# Create .env file
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
```
Never commit credentials to version control. See [Security Best Practices](Security-Best-Practices.md).

### Q: Can I use multiple email accounts?
**A:** Yes! Create separate `EmailConfig` objects for each account:
```python
gmail_config = EmailConfig(smtp_server="smtp.gmail.com", ...)
outlook_config = EmailConfig(smtp_server="smtp-mail.outlook.com", ...)
```

## 📧 Email Sending

### Q: How many emails can I send per day?
**A:** It depends on your email provider:
- **Gmail**: 500 emails/day (free), 2000/day (paid)
- **Outlook**: 300 emails/day (personal), 10,000/day (business)
- **Yahoo**: 500 emails/day
- Check with your provider for current limits

### Q: What's the recommended time interval between emails?
**A:** 
- **5-10 seconds** for most providers (default: 5 seconds)
- **1-2 seconds** minimum to avoid being flagged as spam
- **30+ seconds** for large volumes or if you hit rate limits

### Q: Can I send HTML emails?
**A:** The current version sends plain text emails. However, you can modify the code to send HTML emails. See [Code Examples](Code-Examples.md) for HTML email implementation.

### Q: What's the maximum attachment size?
**A:** Most email providers limit attachments to:
- **Gmail**: 25MB
- **Outlook**: 20MB
- **Yahoo**: 25MB
Consider using cloud storage links for larger files.

## 📋 CSV and Data

### Q: What CSV format is required?
**A:** Your CSV must have an 'email' column. Additional columns become template variables:
```csv
email,name,company,position
john@example.com,John Doe,Tech Corp,Developer
jane@example.com,Jane Smith,Design Inc,Designer
```

### Q: Can I use Excel files instead of CSV?
**A:** No, the application requires CSV format. You can:
1. Save Excel files as CSV in Excel/Google Sheets
2. Install `pandas` and `openpyxl` to convert programmatically

### Q: How do I handle special characters in CSV files?
**A:** Save your CSV files with UTF-8 encoding:
- **Excel**: Save As → CSV UTF-8
- **Google Sheets**: Download as CSV (automatically UTF-8)
- **Text editors**: Save with UTF-8 encoding

### Q: Can I use different CSV files for different email campaigns?
**A:** Yes! Just specify different CSV files when calling `send_bulk_emails()`.

## 📎 File Attachments

### Q: What file types can I attach?
**A:** Any file type is supported:
- Documents: PDF, DOC, DOCX, TXT
- Images: JPG, PNG, GIF
- Spreadsheets: XLS, XLSX, CSV
- Archives: ZIP, RAR
- Any other file type

### Q: How do I attach multiple files?
**A:** Pass a list of file paths:
```python
attachments=["document.pdf", "image.jpg", "spreadsheet.xlsx"]
```

### Q: Can different recipients get different attachments?
**A:** The current bulk email feature sends the same attachments to all recipients. For different attachments per recipient, you'd need to send individual emails in a loop.

### Q: What if an attachment file is missing?
**A:** The application will log a warning and continue sending the email without that attachment. Other attachments will still be included.

## 🔧 Troubleshooting

### Q: Why are my emails going to spam?
**A:** Common reasons and solutions:
1. **Sending too fast**: Increase time intervals
2. **Poor email content**: Avoid spam trigger words
3. **No SPF/DKIM**: Use authenticated email addresses
4. **High volume**: Start with smaller batches
5. **Suspicious attachments**: Be careful with executable files

### Q: The application seems slow. How can I speed it up?
**A:** 
1. **Reduce time intervals** (but don't go below 1 second)
2. **Remove large attachments** or compress them
3. **Process in smaller batches**
4. **Use faster internet connection**

### Q: I'm getting "Connection timed out" errors. What should I do?
**A:** 
1. **Check internet connection**
2. **Try different SMTP ports** (587, 465, 25)
3. **Check firewall/antivirus settings**
4. **Try from a different network**

### Q: How do I resume sending if the process is interrupted?
**A:** Currently, you need to manually track progress. Consider using the advanced batch processing example in [Code Examples](Code-Examples.md) which includes progress saving and recovery.

## 📊 Templates and Personalization

### Q: How do I personalize emails?
**A:** Use placeholders in your templates that match CSV column names:
```python
subject_template = "Hello {name}!"
body_template = "Dear {name}, greetings from {company}!"
```

### Q: What if a CSV column is missing for some recipients?
**A:** The application will raise a `KeyError`. Ensure all required columns exist for all recipients, or modify the code to handle missing data gracefully.

### Q: Can I use conditional content in templates?
**A:** The basic template system doesn't support conditionals, but you can create custom logic. See [Code Examples](Code-Examples.md) for conditional template examples.

### Q: How do I include today's date in emails?
**A:** Add the date to your CSV data or modify the template in code:
```python
from datetime import datetime
today = datetime.now().strftime("%B %d, %Y")
body_template = f"Today is {today}. Dear {{name}}, ..."
```

## 🚀 Advanced Usage

### Q: Can I schedule emails to be sent later?
**A:** The basic application doesn't include scheduling. You could:
1. Use system cron jobs (Linux/macOS) or Task Scheduler (Windows)
2. Add scheduling logic to the code
3. Use external scheduling tools

### Q: How do I track email opens and clicks?
**A:** The basic application doesn't include tracking. For tracking, you'd need to:
1. Use HTML emails with tracking pixels
2. Use shortened URLs for click tracking
3. Consider professional email services for advanced tracking

### Q: Can I send emails through a proxy?
**A:** Yes, but you'd need to modify the SMTP connection code to support proxy settings. This isn't included in the basic version.

### Q: How do I handle bounced emails?
**A:** The application doesn't automatically handle bounces. You'd need to:
1. Monitor your email account for bounce notifications
2. Implement bounce handling logic
3. Use email services that provide bounce APIs

## 🛠️ Customization

### Q: Can I modify the email format?
**A:** Yes! The code is open and customizable. You can:
1. Add HTML email support
2. Modify the template system
3. Add custom headers
4. Change the MIME structure

### Q: How do I add email priority settings?
**A:** Modify the email creation code to add headers:
```python
msg['X-Priority'] = '1'  # High priority
msg['X-MSMail-Priority'] = 'High'
```

### Q: Can I add company logos or signatures?
**A:** Yes, you can:
1. Add logos as attachments
2. Create HTML templates with embedded images
3. Add text-based signatures to email bodies

## 🔄 Integration

### Q: Can I integrate this with Django/Flask?
**A:** Yes! The email classes can be imported and used in web applications. You might need to handle async processing for large batches.

### Q: How do I integrate with databases instead of CSV?
**A:** Modify the `load_recipients_from_csv()` method to load from your database:
```python
def load_recipients_from_database():
    # Your database query logic here
    return list_of_recipient_dictionaries
```

### Q: Can I use this with APIs?
**A:** Yes! You can call the email sending functions from API endpoints. Consider using background task queues for bulk operations.

## 📈 Performance

### Q: How many emails can I send at once?
**A:** Recommended batch sizes:
- **Small batches**: 10-50 emails (testing)
- **Medium batches**: 50-200 emails (regular use)
- **Large batches**: 200+ emails (use advanced batch processing)

### Q: Why does sending get slower over time?
**A:** Possible reasons:
1. **Email provider rate limiting**
2. **Network congestion**
3. **Large attachment processing**
4. **Memory usage accumulation**

Consider restarting for very large batches or using the batch processing examples.

## 💡 Best Practices

### Q: What are the best practices for bulk emailing?
**A:** 
1. **Start small** - test with yourself first
2. **Use realistic intervals** - don't rush
3. **Monitor logs** - watch for errors
4. **Segment recipients** - don't send to everyone at once
5. **Respect unsubscribes** - maintain clean lists
6. **Follow CAN-SPAM** - include sender info and unsubscribe options

### Q: How do I avoid being marked as spam?
**A:** 
1. **Use authenticated email addresses**
2. **Include proper sender information**
3. **Avoid spam trigger words**
4. **Don't send too frequently**
5. **Provide unsubscribe options**
6. **Use plain text or simple HTML**

### Q: Should I use this for production marketing emails?
**A:** This tool is great for:
- Internal company communications
- Small-scale outreach
- Personal projects
- Testing and development

For large-scale marketing, consider professional email services like:
- Mailchimp
- SendGrid
- Amazon SES
- Constant Contact

## 🆘 Still Need Help?

If your question isn't answered here:

1. **Check the [Troubleshooting Guide](Troubleshooting.md)**
2. **Review [Code Examples](Code-Examples.md)**
3. **Read the [API Reference](API-Reference.md)**
4. **Look at the [Security Best Practices](Security-Best-Practices.md)**

---

**Found a bug or have a suggestion?** Consider contributing to the project or creating an issue with detailed information about your use case!
