# Compliance Audit System

A Flask-based AI-powered application that automates compliance audits for vendor contracts. The system uses Azure OCR and GPT-4 to extract and analyze contract clauses, track compliance requirements, and provide intelligent alerts.

## 🚀 Features

### 1. 📥 PDF Upload & OCR
- Upload scanned PDF contracts
- Automatic text extraction using PyPDF2 for text-based PDFs
- Azure Computer Vision OCR for scanned documents
- Store original files and extracted text in PostgreSQL database

### 2. 🧠 AI-Powered Clause Detection
- Uses Azure GPT-4 to automatically detect and categorize clauses:
  - Regulatory clauses (ISO, FDA, GDP, GMP)
  - Financial obligations and payment terms
  - Penalty clauses for non-compliance
  - Renewal and termination conditions
- Risk assessment for each clause (Low/Medium/High)
- Automatic compliance requirement extraction

### 3. 📊 Compliance Dashboard
- Modern, responsive UI built with Tailwind CSS
- Real-time statistics and visualizations using Chart.js
- Contract compliance status overview
- Risk distribution analysis
- Upcoming audits and expiring contracts

### 4. 🔔 Alerts & Scheduling
- APScheduler runs automated daily checks
- Email notifications for:
  - Contract expiration (30, 60, 90 days notice)
  - Upcoming compliance audits
  - High-risk contract reviews
- Dashboard alerts for immediate attention items

### 5. 📁 Storage & Retrieval
- PostgreSQL database for contract metadata
- Export reports in CSV and PDF formats
- Full audit trail logging
- Secure file storage

### 6. 🔐 Security
- JWT-based authentication
- Role-based access control (Admin, Auditor, Contract Owner)
- Complete audit logging for regulatory compliance
- Secure password hashing with bcrypt

### 7. 💬 Clause-Level Q&A Bot
- Natural language contract queries
- AI-powered answers based on contract content
- Suggested questions for each contract
- Compliance standard verification

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Redis (for Celery task queue)
- Azure Computer Vision API credentials
- Azure OpenAI API credentials

## 🛠️ Installation

1. **Clone the repository**
```bash
cd /workspace/compliance-audit-app
```

2. **Create a virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
```

Edit `.env` file with your configuration:
- Database credentials
- Azure Computer Vision endpoint and key
- Azure OpenAI endpoint and key
- Email server settings
- Secret keys for Flask and JWT

5. **Initialize the database**
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

6. **Run the application**
```bash
python run.py
```

The application will be available at `http://localhost:5000`

## 🔑 Default Credentials

- **Username:** admin
- **Password:** admin123

⚠️ **Important:** Change these credentials immediately in production!

## 📁 Project Structure

```
compliance-audit-app/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── models/              # Database models
│   ├── api/                 # API endpoints
│   ├── services/            # Business logic services
│   ├── templates/           # HTML templates
│   ├── static/              # Static files
│   └── utils/               # Utility functions
├── config/
│   └── config.py           # Configuration classes
├── migrations/             # Database migrations
├── tests/                  # Test files
├── requirements.txt        # Python dependencies
├── run.py                  # Application entry point
└── README.md              # This file
```

## 🔧 Configuration

### Azure Computer Vision
1. Create a Computer Vision resource in Azure Portal
2. Copy the endpoint and key to `.env` file

### Azure OpenAI
1. Create an OpenAI resource in Azure Portal
2. Deploy a GPT-4 model
3. Copy the endpoint, key, and deployment name to `.env` file

### Email Configuration
Configure SMTP settings in `.env` for email notifications:
```
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

## 📚 API Documentation

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Refresh access token
- `GET /api/auth/profile` - Get user profile

### Contracts
- `GET /api/contracts` - List contracts with filtering
- `POST /api/contracts` - Upload new contract
- `GET /api/contracts/{id}` - Get contract details
- `PUT /api/contracts/{id}` - Update contract
- `DELETE /api/contracts/{id}` - Delete contract
- `GET /api/contracts/{id}/download` - Download original PDF
- `POST /api/contracts/{id}/audit` - Mark as audited

### Clauses
- `GET /api/clauses` - List clauses with filtering
- `GET /api/clauses/{id}` - Get clause details
- `PUT /api/clauses/{id}` - Update clause
- `POST /api/clauses/{id}/review` - Mark as reviewed

### Chat/Q&A
- `POST /api/chat/ask` - Ask question about contract
- `GET /api/chat/contract/{id}/summary` - Get AI summary
- `GET /api/chat/suggested-questions` - Get suggested questions

### Reports
- `GET /api/reports/contracts/csv` - Export contracts as CSV
- `GET /api/reports/contract/{id}/pdf` - Export contract report as PDF
- `GET /api/reports/dashboard-stats` - Get dashboard statistics

## 🚀 Production Deployment

### Using Gunicorn
```bash
gunicorn -w 4 -b 0.0.0.0:8000 run:app
```

### Using Docker
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "run:app"]
```

### Environment Variables for Production
- Set `FLASK_ENV=production`
- Use strong secret keys
- Configure production database
- Set up proper email server
- Use HTTPS in production

## 🧪 Testing

Run tests with pytest:
```bash
pytest tests/
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
- Create an issue in the repository
- Contact the development team

## 🔮 Future Enhancements

- Multi-language support
- Advanced analytics dashboard
- Integration with more AI models
- Mobile application
- Blockchain integration for contract verification
- Advanced workflow automation