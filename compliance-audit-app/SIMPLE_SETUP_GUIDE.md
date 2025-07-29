# Super Simple Setup Guide

## You Only Need ONE Thing: Your OpenAI API Key!

### Step 1: Run the Setup Script
```bash
cd /workspace/compliance-audit-app
./simple_setup.sh
```

### Step 2: Add Your OpenAI API Key
Edit the `.env` file and replace `sk-YOUR-OPENAI-API-KEY-HERE` with your actual OpenAI API key:
```bash
nano .env
```

Your .env file should look like:
```
OPENAI_API_KEY=sk-proj-abcd1234... (your actual key)
```

### Step 3: Run the App
```bash
source venv/bin/activate
python run.py
```

### Step 4: Use the App
1. Open browser: http://localhost:5000
2. Login with: **admin** / **admin123**
3. Upload PDF contracts
4. The system will analyze them using GPT-4

## That's It! 🎉

### What This Setup Gives You:
- ✅ **No complex configuration** - JWT keys are auto-generated
- ✅ **No database setup** - Uses SQLite automatically
- ✅ **No Azure needed** - Uses your OpenAI API directly
- ✅ **PDF text extraction** - Works automatically
- ✅ **AI contract analysis** - Using GPT-4

### Optional Features (Can Add Later):
- Email notifications (need SMTP setup)
- OCR for scanned PDFs (need Azure Computer Vision)
- Background tasks (need Redis)

### Troubleshooting:
1. **"No module named X"** - Run: `pip install -r requirements.txt`
2. **"OpenAI API error"** - Check your API key is correct
3. **"Port 5000 in use"** - Change PORT in .env file

### Important Notes:
- The system auto-generates secure keys - you don't need to understand JWT!
- Default admin password is **admin123** - change it after first login
- All uploaded contracts are stored in `app/static/uploads/`
- Database is stored in `compliance_audit.db` file