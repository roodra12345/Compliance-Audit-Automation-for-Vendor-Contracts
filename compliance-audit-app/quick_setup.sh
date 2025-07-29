#!/bin/bash

echo "=== Compliance Audit System - Quick Setup ==="
echo

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✓ Created .env file - Please edit it with your credentials!"
else
    echo "✓ .env file already exists"
fi

# Create upload directory
echo "Creating upload directory..."
mkdir -p app/static/uploads
chmod 755 app/static/uploads

# Generate secret keys
echo
echo "=== Generating secure secret keys ==="
echo "Add these to your .env file:"
echo
echo "SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')"
echo "JWT_SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')"
echo

# Check for PostgreSQL
if command -v psql &> /dev/null; then
    echo "✓ PostgreSQL is installed"
    echo "To create database, run:"
    echo "  sudo -u postgres createdb compliance_audit_db"
    echo "  sudo -u postgres createuser -P your_username"
else
    echo "⚠ PostgreSQL not found - Using SQLite for development"
fi

# Check for Redis
if command -v redis-cli &> /dev/null; then
    echo "✓ Redis is installed"
else
    echo "⚠ Redis not found - Background tasks will not work"
fi

echo
echo "=== Next Steps ==="
echo "1. Edit .env file with your Azure credentials"
echo "2. Initialize database: flask db upgrade"
echo "3. Run the app: python run.py"
echo
echo "Default login: admin / admin123"
echo "IMPORTANT: Change the admin password after first login!"