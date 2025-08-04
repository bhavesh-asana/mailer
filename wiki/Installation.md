# Installation Guide

This guide will help you install and set up the Email Mailer Application on your system.

## 📋 Prerequisites

- **Python 3.7 or higher** (Python 3.8+ recommended)
- **Internet connection** for email sending
- **Email account** (Gmail, Outlook, Yahoo, or custom SMTP)

## 🛠️ Installation Steps

### 1. Download/Clone the Project

```bash
# If using Git
git clone https://github.com/your-username/mailer.git
cd mailer

# Or download and extract the ZIP file
```

### 2. Check Python Version

```bash
python --version
# or
python3 --version
```

Make sure you have Python 3.7 or higher installed.

### 3. Install Dependencies (Optional)

The mailer application uses only Python built-in modules for core functionality. However, you can install optional packages for enhanced features:

```bash
# Install optional dependencies
pip install -r requirements.txt

# Or install individual packages
pip install python-dotenv  # For .env file support
pip install pandas         # For advanced CSV handling
```

### 4. Verify Installation

Run the test script to verify everything is working:

```bash
python test_mailer.py
```

You should see output indicating that the CSV loading and template functionality work correctly.

## 🔧 Platform-Specific Setup

### Windows

1. **Install Python** from [python.org](https://www.python.org/downloads/)
2. **Open Command Prompt** or PowerShell
3. Navigate to the mailer directory
4. Run the commands above

```cmd
# Windows Command Prompt
cd C:\path\to\mailer
python mail.py
```

### macOS

1. **Python is pre-installed** on macOS (but may be older version)
2. **Install newer Python** via Homebrew (recommended):
   ```bash
   brew install python3
   ```
3. **Open Terminal**
4. Navigate to the mailer directory
5. Run the commands above

```bash
# macOS Terminal
cd /Users/YourName/Developer/mailer
python3 mail.py
```

### Linux (Ubuntu/Debian)

1. **Update package list**:
   ```bash
   sudo apt update
   ```
2. **Install Python 3** (if not installed):
   ```bash
   sudo apt install python3 python3-pip
   ```
3. **Navigate to project directory**
4. Run the commands above

```bash
# Linux Terminal
cd /home/yourusername/mailer
python3 mail.py
```

## 📁 Project Structure After Installation

```
mailer/
├── mail.py                    # Main application
├── test_mailer.py            # Test script
├── example_usage.py          # Usage examples
├── recipients.csv            # Sample data
├── requirements.txt          # Dependencies
├── .gitignore               # Git ignore rules
├── README.md                # Documentation
├── GMAIL_SETUP.md           # Gmail setup guide
└── wiki/                    # Documentation folder
    └── ... (wiki pages)
```

## ✅ Verification Steps

### 1. Test CSV Loading

```bash
python -c "from mail import EmailSender; print('CSV loading works!')"
```

### 2. Test Template System

```bash
python test_mailer.py
```

### 3. Test Email Configuration (without sending)

```bash
python -c "
from mail import EmailConfig
config = EmailConfig('smtp.gmail.com', 587, 'test@test.com', 'password')
print('Configuration works!')
"
```

## 🐛 Common Installation Issues

### Issue: `ModuleNotFoundError`

**Solution**: Make sure you're in the correct directory
```bash
cd /path/to/mailer
ls  # Should show mail.py and other files
```

### Issue: `Permission Denied` (Linux/macOS)

**Solution**: Use `sudo` or check file permissions
```bash
chmod +x mail.py
python3 mail.py
```

### Issue: Python Not Found

**Solution**: 
- **Windows**: Add Python to PATH during installation
- **macOS**: Use `python3` instead of `python`
- **Linux**: Install Python 3: `sudo apt install python3`

### Issue: `pip` Command Not Found

**Solution**:
```bash
# Windows
python -m pip install package_name

# macOS/Linux
python3 -m pip install package_name
```

## 🔄 Virtual Environment (Recommended)

For better dependency management, use a virtual environment:

```bash
# Create virtual environment
python -m venv email_env

# Activate virtual environment
# Windows:
email_env\Scripts\activate
# macOS/Linux:
source email_env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Deactivate when done
deactivate
```

## 📦 Optional Enhancements

### 1. Install python-dotenv for .env files

```bash
pip install python-dotenv
```

Then create a `.env` file for secure credential storage:
```
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

### 2. Install pandas for advanced CSV handling

```bash
pip install pandas
```

### 3. Install openpyxl for Excel support

```bash
pip install openpyxl
```

## ✅ Installation Complete!

Once installation is complete, proceed to:

1. **[Configuration Guide](Configuration.md)** - Set up your email provider
2. **[Quick Start Tutorial](Quick-Start-Tutorial.md)** - Send your first email
3. **[Basic Usage](Basic-Usage.md)** - Learn the core features

## 📞 Need Help?

If you encounter issues during installation:

1. Check the **[Troubleshooting Guide](Troubleshooting.md)**
2. Verify you have the correct Python version
3. Make sure you're in the right directory
4. Check file permissions on Linux/macOS

---

**Next Step**: [Configure your email provider](Configuration.md) to start sending emails!
