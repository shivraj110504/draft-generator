# 🚀 NyaySetu Complete Deployment Guide

## 📁 Step 1: Project Setup

### Create Project Structure

```bash
# Create main directory
mkdir nyaysetu-app
cd nyaysetu-app

# Create subdirectories
mkdir -p backend/generators backend/config backend/outputs backend/utils
mkdir -p frontend/css frontend/js

# Create __init__.py files for Python modules
touch backend/__init__.py
touch backend/generators/__init__.py
touch backend/utils/__init__.py
```

### Place Files in Correct Locations

```
nyaysetu-app/
├── backend/
│   ├── app.py                          # Main Flask application
│   ├── generators/
│   │   ├── __init__.py
│   │   ├── rti_generator.py            # RTI generator module
│   │   ├── affidavit_generator.py      # Affidavit generator
│   │   └── orchestrator.py             # AI orchestrator
│   ├── config/
│   │   └── jurisdiction_rules.json     # State rules database
│   └── outputs/                        # Generated PDFs (auto-created)
├── frontend/
│   └── index.html                      # Frontend UI
├── requirements.txt                     # Python dependencies
├── runtime.txt                         # Python version for Render
├── .env                                # Environment variables
└── README.md                           # Documentation
```

---

## 💻 Step 2: Local Development Setup

### Install Python Dependencies

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Mac/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Create `.env` File

```bash
# Create .env in root directory
cat > .env << 'EOF'
FLASK_APP=backend/app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-change-this
PORT=5000
EOF
```

### Run Backend Locally

```bash
# From nyaysetu-app directory
cd backend
python app.py

# Server will start at http://localhost:5000
```

### Test API

```bash
# In another terminal, test the API
curl http://localhost:5000/

# Should return:
# {"status": "success", "message": "NyaySetu API v2.0", ...}
```

### Open Frontend Locally

```bash
# Option 1: Python HTTP server
cd frontend
python3 -m http.server 8000

# Open browser: http://localhost:8000

# Option 2: Just open index.html in browser
# But remember to update API_URL in index.html to http://localhost:5000
```

---

## 🌐 Step 3: Deploy to Render

### Prepare for Render Deployment

#### Create `runtime.txt`

```bash
cat > runtime.txt << 'EOF'
python-3.11.0
EOF
```

#### Create `render.yaml` (Optional but recommended)

```bash
cat > render.yaml << 'EOF'
services:
  - type: web
    name: nyaysetu-backend
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "gunicorn --bind 0.0.0.0:$PORT backend.app:app"
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: SECRET_KEY
        generateValue: true
EOF
```

#### Update `requirements.txt` if needed

Ensure it has:
```
Flask==3.0.0
Flask-CORS==4.0.0
reportlab==4.0.9
pypdf==4.0.1
python-dotenv==1.0.0
gunicorn==21.2.0
Werkzeug==3.0.1
```

### Deploy Backend to Render

1. **Push to GitHub**

```bash
# Initialize git
git init
git add .
git commit -m "Initial commit - NyaySetu v2.0"

# Create new repository on GitHub (github.com)
# Then:
git remote add origin https://github.com/yourusername/nyaysetu-app.git
git branch -M main
git push -u origin main
```

2. **Create Render Account**
   - Go to [render.com](https://render.com)
   - Sign up / Sign in with GitHub

3. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Configure:
     - **Name**: `nyaysetu-backend`
     - **Environment**: `Python 3`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT backend.app:app`
     - **Instance Type**: Free

4. **Set Environment Variables**
   - In Render dashboard, go to "Environment"
   - Add:
     - `SECRET_KEY`: (generate a random string)
     - `PYTHON_VERSION`: `3.11.0`

5. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment (5-10 minutes)
   - You'll get a URL like: `https://nyaysetu-backend.onrender.com`

6. **Test Deployed API**

```bash
curl https://nyaysetu-backend.onrender.com/

# Should return success message
```

### Deploy Frontend to Render (Static Site)

1. **Create New Static Site**
   - In Render dashboard: "New +" → "Static Site"
   - Connect same GitHub repo
   - Configure:
     - **Name**: `nyaysetu-frontend`
     - **Build Command**: (leave empty)
     - **Publish Directory**: `frontend`

2. **Update Frontend API URL**

Before deploying, update `index.html`:

```javascript
// Change this line in index.html
const API_URL = 'https://nyaysetu-backend.onrender.com';
```

3. **Deploy**
   - Commit and push changes
   - Render will auto-deploy
   - You'll get: `https://nyaysetu-frontend.onrender.com`

---

## 🔧 Step 4: Configuration & Testing

### Update CORS Settings

In `backend/app.py`, update CORS:

```python
from flask_cors import CORS

# Update this line:
CORS(app, origins=['https://nyaysetu-frontend.onrender.com'])
```

### Test Full Flow

1. **Open frontend**: `https://nyaysetu-frontend.onrender.com`
2. **Try AI Analysis**:
   - Go to "AI Analysis" tab
   - Enter: "I need RTI for exam records"
   - Click "Analyze Requirement"
   - Should show complexity score and suggestions

3. **Generate RTI**:
   - Fill in RTI form
   - Click "Generate RTI Application"
   - Should download PDF

4. **Generate Affidavit**:
   - Go to "Affidavit" tab
   - Fill form with 3+ statements
   - Click "Generate Affidavit"
   - Should download PDF

---

## 🐛 Troubleshooting

### Issue: API Returns 404

**Solution**: Check CORS settings and API_URL in frontend

```javascript
// In index.html, verify:
const API_URL = 'https://your-actual-backend-url.onrender.com';
```

### Issue: Import Errors in Backend

**Solution**: Ensure __init__.py files exist:

```bash
touch backend/__init__.py
touch backend/generators/__init__.py
```

### Issue: PDF Generation Fails

**Solution**: Check logs in Render dashboard:
- Go to your service → "Logs"
- Look for errors related to reportlab or file permissions

### Issue: Render Deployment Timeout

**Solution**: 
1. Check `requirements.txt` for heavy packages
2. Ensure build command is correct
3. Free tier has limited resources - upgrade if needed

---

## 📊 Monitoring & Logs

### View Logs on Render

1. Go to your service in Render dashboard
2. Click "Logs" tab
3. You'll see real-time logs

### Add Logging to Your App

Update `backend/app.py`:

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/api/generate/rti', methods=['POST'])
def generate_rti():
    logger.info("RTI generation request received")
    # ... rest of code
```

---

## 🔒 Security Best Practices

### 1. Environment Variables

Never commit `.env` to git:

```bash
echo ".env" >> .gitignore
echo "venv/" >> .gitignore
echo "*.pyc" >> .gitignore
echo "__pycache__/" >> .gitignore
echo "backend/outputs/*.pdf" >> .gitignore
```

### 2. API Rate Limiting

Add to `backend/app.py`:

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)

@app.route('/api/generate/rti', methods=['POST'])
@limiter.limit("10 per hour")
def generate_rti():
    # ... code
```

Add to requirements.txt:
```
Flask-Limiter==3.5.0
```

---

## 📈 Scaling & Optimization

### Database for Document History

```bash
pip install flask-sqlalchemy

# Update requirements.txt
echo "Flask-SQLAlchemy==3.1.1" >> requirements.txt
```

Add to `backend/app.py`:

```python
from flask_sqlalchemy import SQLAlchemy

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///documents.db'
db = SQLAlchemy(app)

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doc_hash = db.Column(db.String(64), unique=True)
    doc_type = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

### File Storage (S3 or Cloud Storage)

For production, store PDFs in cloud storage:

```bash
pip install boto3  # For AWS S3
```

---

## 🎯 Complete Deployment Checklist

- [ ] Project structure created
- [ ] All files in correct locations
- [ ] __init__.py files created
- [ ] requirements.txt updated
- [ ] runtime.txt created
- [ ] .env file created (not committed)
- [ ] .gitignore configured
- [ ] Code tested locally
- [ ] GitHub repository created
- [ ] Code pushed to GitHub
- [ ] Render account created
- [ ] Backend deployed to Render
- [ ] Backend URL obtained
- [ ] Frontend API_URL updated
- [ ] Frontend deployed to Render
- [ ] CORS configured
- [ ] End-to-end tested
- [ ] Logs checked
- [ ] Error handling verified

---

## 🚀 Quick Start Commands

```bash
# Clone or setup
git clone https://github.com/yourusername/nyaysetu-app.git
cd nyaysetu-app

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run locally
cd backend
python app.py

# In another terminal - run frontend
cd frontend
python3 -m http.server 8000

# Open browser
# Backend: http://localhost:5000
# Frontend: http://localhost:8000
```

---

## 📞 Support & Resources

- **Render Docs**: https://render.com/docs
- **Flask Docs**: https://flask.palletsprojects.com/
- **ReportLab Docs**: https://www.reportlab.com/docs/

---

## 🎓 What You've Built

✅ **Full-stack application** with Flask backend + HTML frontend
✅ **RESTful API** with multiple endpoints
✅ **AI-powered analysis** for document suggestions
✅ **PDF generation** with legal formatting
✅ **Blockchain hashing** for document verification
✅ **Production deployment** on Render
✅ **Scalable architecture** ready for expansion

**Congratulations! Your NyaySetu app is live! 🎉**
