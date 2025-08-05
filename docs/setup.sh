#!/bin/bash

# Mailer Service Setup Script
# This script sets up the development environment for the mailer service

echo "🚀 Setting up Mailer Service..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check if pip is installed
if ! command -v pip &> /dev/null; then
    echo "❌ pip is required but not installed."
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚙️  Creating .env file from template..."
    cp .env.example .env
    echo "🔧 Please edit .env file with your email configuration before proceeding."
    echo "📧 Required: SMTP_SERVER, SMTP_PORT, EMAIL_USERNAME, EMAIL_PASSWORD"
    read -p "Press enter after configuring .env file..."
fi

# Clean up any existing database (optional - comment out if you want to keep existing data)
# echo "🗄️  Cleaning up existing database..."
# rm -f db.sqlite3

# Run migrations to create/update database
echo "🗄️  Setting up SQLite database..."
python manage.py makemigrations
python manage.py migrate

# Create default email configuration
echo "📧 Creating default email configuration..."
python manage.py setup_default_email_config

# Collect static files (useful for production)
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Ask if user wants to create superuser
read -p "🔐 Create Django admin superuser? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python manage.py createsuperuser
fi

echo ""
echo "✅ Setup complete!"
echo "📋 Database: SQLite (db.sqlite3) - ready to use"
echo ""
echo "🚀 To start the server, run:"
echo "   python manage.py runserver"
echo ""
echo "📖 Available endpoints:"
echo "   http://127.0.0.1:8000/swagger/     - API Documentation"
echo "   http://127.0.0.1:8000/admin/       - Django Admin"
echo "   http://127.0.0.1:8000/api/health/  - Health Check"
echo "   http://127.0.0.1:8000/api/stats/   - Email Statistics"
echo ""
echo "📧 Test the API:"
echo "   curl -X POST http://127.0.0.1:8000/api/send-email/ \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"to_email\":\"test@example.com\",\"subject\":\"Test\",\"body\":\"Hello!\"}'"
echo ""
echo "📚 For more information, visit: https://github.com/bhavesh-asana/mailer/wiki"
