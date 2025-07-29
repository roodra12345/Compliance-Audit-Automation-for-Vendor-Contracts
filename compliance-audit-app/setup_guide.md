# Compliance Audit System - Setup Guide

## Prerequisites

Before setting up the system, ensure you have:

1. **Python 3.8+** installed
2. **PostgreSQL 12+** installed (or use SQLite for development)
3. **Redis** (optional, for background tasks)
4. **Azure Account** with:
   - Computer Vision resource
   - OpenAI resource with GPT-4 deployment

## Step-by-Step Setup

### 1. Install Dependencies

```bash
cd /workspace/compliance-audit-app

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python packages
pip install -r requirements.txt
```

### 2. Set Up Database

#### Option A: PostgreSQL (Recommended)
```bash
# Install PostgreSQL if not already installed
sudo apt-get install postgresql postgresql-contrib

# Create database
sudo -u postgres psql
CREATE DATABASE compliance_audit_db;
CREATE USER your_username WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE compliance_audit_db TO your_username;
\q
```

#### Option B: SQLite (Development only)
No setup needed - SQLite database will be created automatically.

### 3. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file with your actual values
nano .env  # or use your preferred editor
```

### 4. Get Azure Credentials

#### Azure Computer Vision (for OCR):
1. Go to [Azure Portal](https://portal.azure.com)
2. Create a new "Computer Vision" resource
3. Go to "Keys and Endpoint"
4. Copy:
   - Endpoint → `AZURE_COMPUTER_VISION_ENDPOINT`
   - Key 1 or Key 2 → `AZURE_COMPUTER_VISION_KEY`

#### Azure OpenAI (for AI analysis):
1. Go to [Azure Portal](https://portal.azure.com)
2. Create a new "Azure OpenAI" resource
3. Go to "Keys and Endpoint"
4. Copy:
   - Endpoint → `AZURE_OPENAI_ENDPOINT`
   - Key 1 or Key 2 → `AZURE_OPENAI_KEY`
5. Deploy a GPT-4 model in Azure OpenAI Studio
6. Copy deployment name → `AZURE_OPENAI_DEPLOYMENT_NAME`

### 5. Configure Email (Optional)

For Gmail:
1. Enable 2-factor authentication
2. Generate an app-specific password
3. Use this password in `MAIL_PASSWORD`

### 6. Initialize Database

```bash
# Set Flask app
export FLASK_APP=run.py

# Initialize migrations
flask db init

# Create migration
flask db migrate -m "Initial migration"

# Apply migration
flask db upgrade
```

### 7. Run the Application

```bash
# Development mode
python run.py

# Production mode with Gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 run:app
```

### 8. Access the Application

1. Open browser: `http://localhost:5000`
2. Login with default credentials:
   - Username: `admin`
   - Password: `admin123`
3. **IMPORTANT**: Change the admin password immediately!

## Required Environment Variables Summary

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Flask secret key | `generate-a-random-string` |
| `JWT_SECRET_KEY` | JWT token secret | `another-random-string` |
| `DATABASE_URL` | Database connection string | `postgresql://user:pass@localhost/db` |
| `AZURE_COMPUTER_VISION_ENDPOINT` | Azure CV endpoint | `https://myresource.cognitiveservices.azure.com/` |
| `AZURE_COMPUTER_VISION_KEY` | Azure CV API key | `your-32-char-key` |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint | `https://myopenai.openai.azure.com/` |
| `AZURE_OPENAI_KEY` | Azure OpenAI API key | `your-32-char-key` |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | GPT-4 deployment name | `gpt-4` |

## Optional Services

### Redis (for background tasks)
```bash
# Install Redis
sudo apt-get install redis-server

# Start Redis
redis-server
```

### Email Notifications
Configure SMTP settings in .env file for email alerts.

## Troubleshooting

### Common Issues:

1. **Database connection error**
   - Check PostgreSQL is running: `sudo service postgresql status`
   - Verify credentials in DATABASE_URL

2. **Azure API errors**
   - Verify endpoints include trailing slash
   - Check API keys are correct
   - Ensure resources are deployed in Azure

3. **File upload errors**
   - Check upload folder exists and has write permissions
   - Verify PDF file size is under 16MB

4. **Email not sending**
   - Check firewall allows SMTP port (587)
   - Verify email credentials
   - For Gmail, use app-specific password

## Testing the Setup

1. **Test Database**: Try logging in with admin credentials
2. **Test OCR**: Upload a sample PDF contract
3. **Test AI**: Check if clauses are detected after upload
4. **Test Email**: Trigger a test alert

## Security Checklist

- [ ] Change default admin password
- [ ] Generate strong SECRET_KEY and JWT_SECRET_KEY
- [ ] Use HTTPS in production
- [ ] Configure firewall rules
- [ ] Set FLASK_ENV=production
- [ ] Use environment-specific .env files
- [ ] Regularly update dependencies