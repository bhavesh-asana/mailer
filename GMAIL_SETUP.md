# Gmail App Password Setup Guide

## Step-by-Step Instructions to Setup Gmail App Password

### 1. Enable 2-Factor Authentication (2FA)
1. Go to your Google Account settings: https://myaccount.google.com/
2. Click on "Security" in the left sidebar
3. Under "Signing in to Google", click on "2-Step Verification"
4. Follow the prompts to enable 2FA (you'll need your phone)

### 2. Generate App Password
1. After enabling 2FA, go back to Security settings
2. Under "Signing in to Google", click on "App passwords"
3. You might need to sign in again
4. Select "Mail" from the "Select app" dropdown
5. Select "Other (Custom name)" from the "Select device" dropdown
6. Enter a name like "Python Mailer" or "Email Script"
7. Click "Generate"
8. **IMPORTANT**: Copy the 16-character app password that appears
   - It will look like: `abcd efgh ijkl mnop` (with spaces)
   - You can remove the spaces when using it: `abcdefghijklmnop`

### 3. Use App Password in the Script
- Use this app password instead of your regular Gmail password
- Keep it secure and don't share it

### 4. Alternative: Use Environment Variables (Recommended)
Create a `.env` file in your project directory:

```
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password_here
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

Then modify the script to use environment variables for better security.

### 5. Test Again
Once you have the app password, run the test script again:
```bash
python test_mailer.py
```

## Troubleshooting

### Error: "Application-specific password required"
- This means you need to create an App Password (see steps above)
- Your regular Gmail password won't work

### Error: "Username and Password not accepted"
- Double-check your email address
- Make sure you're using the App Password, not regular password
- Ensure 2FA is enabled on your Google account

### Error: "SMTPAuthenticationError"
- Verify your credentials
- Try generating a new App Password
- Make sure "Less secure app access" is NOT enabled (it's deprecated)

### Still having issues?
- Make sure you're using the correct SMTP settings:
  - Server: smtp.gmail.com
  - Port: 587
  - TLS: Enabled
- Check if your Google account has any security restrictions
- Try using a different email provider for testing (like Outlook)

## Alternative Email Providers

### Outlook/Hotmail
```
SMTP Server: smtp-mail.outlook.com
Port: 587
TLS: Yes
Username: your_email@outlook.com
Password: your_regular_password (no app password needed)
```

### Yahoo
```
SMTP Server: smtp.mail.yahoo.com
Port: 587
TLS: Yes
Username: your_email@yahoo.com
Password: App Password (similar to Gmail process)
```
