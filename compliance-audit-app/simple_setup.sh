#!/bin/bash

echo "=== Simple Setup for Compliance Audit System ==="
echo "This setup requires only your OpenAI API key!"
echo

# Check Python version
python3 --version

# Create virtual environment
echo "Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing required packages..."
pip install -r requirements.txt

# Create .env file
echo "Creating configuration file..."
cat > .env << EOL
# Basic Configuration
FLASK_ENV=development
DATABASE_URL=sqlite:///compliance_audit.db

# Your OpenAI API Key (REQUIRED)
# Get it from: https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-YOUR-OPENAI-API-KEY-HERE

# Everything else is optional and auto-configured
EOL

# Create necessary directories
mkdir -p app/static/uploads

echo
echo "=== SETUP COMPLETE! ==="
echo
echo "Next steps:"
echo "1. Edit .env file and add your OpenAI API key:"
echo "   nano .env"
echo
echo "2. Run the application:"
echo "   source venv/bin/activate"
echo "   python run.py"
echo
echo "3. Open browser to: http://localhost:5000"
echo "   Login: admin / admin123"
echo
echo "That's it! The system will:"
echo "- Auto-generate secure keys"
echo "- Use SQLite database (no setup needed)"
echo "- Extract text from PDFs using PyPDF2"
echo "- Analyze contracts using your OpenAI GPT-4 API"