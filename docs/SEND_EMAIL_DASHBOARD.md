# Send Email Dashboard

The **Send Email Dashboard** is a powerful admin interface feature that allows you to create, schedule, and manage email campaigns with ease.

## Features

### 📧 Email Campaign Creation
- **Template Selection**: Choose from existing email templates with rich content and attachments
- **Recipient Management**: Select multiple recipients from your contact list
- **Time Scheduling**: Schedule emails for immediate sending or future dates
- **Recurring Intervals**: Set up recurring campaigns (hourly, daily, weekly, monthly)

### 🎯 Template Integration
- **Live Preview**: Preview templates with sample data before sending
- **Attachment Support**: Templates automatically include their associated attachments
- **Variable Substitution**: Automatic replacement of placeholder variables with recipient data
- **Test Email**: Send test emails to verify template appearance

### ⏰ Scheduling Options
- **Send Once**: Send emails immediately or at a specific time
- **Hourly**: Send every hour (great for reminders)
- **Daily**: Send once per day
- **Weekly**: Send once per week
- **Monthly**: Send once per month
- **End Date**: Set an optional end date for recurring campaigns

### 📊 Campaign Management
- **Status Tracking**: Monitor campaign status (Draft, Scheduled, Active, Completed, etc.)
- **Statistics**: Track sent/failed email counts
- **Campaign Actions**: Pause, resume, or cancel campaigns
- **Send Now**: Force send campaigns immediately

## How to Access

1. Log into the Django Admin interface
2. Navigate to **Email API** → **Scheduled Email Campaigns**
3. Click the **"📧 Send Email Dashboard"** button

## Quick Start Guide

### 1. Create an Email Template
1. Go to **Email Templates** in the admin
2. Create a new template with subject and body content
3. Use placeholders like `$name`, `$first_name`, `$email` for personalization
4. Optionally attach files using the **Template Attachments** section

### 2. Add Recipients
1. Go to **Recipients** in the admin
2. Add recipients manually or use **Bulk Import** for CSV/Excel files
3. Ensure recipients are marked as **Active**

### 3. Create a Campaign
1. Open the **Send Email Dashboard**
2. Fill in the campaign form:
   - **Name**: Give your campaign a descriptive name
   - **Template**: Select your email template
   - **Recipients**: Choose who should receive the email
   - **Interval**: Choose sending frequency
   - **Scheduled Time**: When to start sending
   - **End Time**: When to stop (for recurring campaigns)

### 4. Preview and Test
1. Use the **"👁️ Preview"** button to see how your email will look
2. Send a **test email** to yourself before launching the campaign
3. Review attached files in the preview

### 5. Launch Campaign
1. Click **"🚀 Create Campaign"** to schedule the email
2. Monitor progress in the **Recent Campaigns** section
3. Use campaign actions to pause, resume, or cancel as needed

## Template Variables

The dashboard supports automatic variable substitution:

| Variable | Description | Example |
|----------|-------------|---------|
| `$name` | Recipient's display name | "John Doe" |
| `$first_name` | First name | "John" |
| `$last_name` | Last name | "Doe" |
| `$email` | Email address | "john@example.com" |
| `$company` | Company name | "Acme Corp" |

## Automation

### Scheduled Sending
Set up a cron job to automatically send scheduled campaigns:

```bash
# Add to crontab (run every 5 minutes)
*/5 * * * * cd /path/to/mailer && python manage.py send_scheduled_emails

# Or run manually
python manage.py send_scheduled_emails

# Dry run to see what would be sent
python manage.py send_scheduled_emails --dry-run
```

## Best Practices

### 📧 Email Templates
- Keep subject lines under 50 characters
- Test templates with different recipient data
- Use responsive HTML for mobile compatibility
- Include unsubscribe links for compliance

### 👥 Recipient Management
- Regularly clean up inactive recipients
- Use meaningful groups/tags for targeting
- Verify email addresses before adding

### ⏰ Scheduling
- Avoid peak hours for better deliverability
- Consider time zones for your audience
- Use end dates for promotional campaigns
- Monitor bounce rates and adjust

### 📊 Monitoring
- Check campaign statistics regularly
- Review email logs for delivery issues
- Pause campaigns if bounce rates are high
- Use A/B testing with different templates

## Troubleshooting

### Common Issues

**Emails not sending:**
- Check SMTP configuration in Django settings
- Verify email credentials are correct
- Ensure recipients are marked as active

**Template variables not replaced:**
- Check variable names match exactly
- Ensure recipient data is complete
- Test with sample data first

**Attachments not included:**
- Verify files exist on the server
- Check file permissions
- Ensure template attachments are properly linked

**Dashboard not accessible:**
- Verify admin permissions
- Check Django admin URLs configuration
- Ensure migrations are applied

## Support

For additional help:
- Check the Django admin logs
- Review email server logs
- Use the test email feature to diagnose issues
- Contact your system administrator for SMTP configuration

---

*This dashboard provides a user-friendly interface for managing complex email campaigns while maintaining the power and flexibility of the underlying Django email system.*
