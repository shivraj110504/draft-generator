# 📂 NyaySetu - Complete File Organization Guide

## 🎯 Where to Place Each File

### Step-by-Step File Organization

#### 1. Create Root Directory Structure

```bash
mkdir nyaysetu-app
cd nyaysetu-app
```

#### 2. Create Backend Structure

```bash
mkdir -p backend/generators backend/config backend/outputs backend/utils
```

#### 3. Create Frontend Structure

```bash
mkdir -p frontend/css frontend/js frontend/assets
```

#### 4. Place Downloaded Files

After downloading all files from this session, organize them as follows:

```
YOUR_DOWNLOADS/
├── app.py                          → nyaysetu-app/backend/app.py
├── rti_generator.py                → nyaysetu-app/backend/generators/rti_generator.py
├── affidavit_generator_backend.py  → nyaysetu-app/backend/generators/affidavit_generator.py
├── orchestrator.py                 → nyaysetu-app/backend/generators/orchestrator.py
├── jurisdiction_rules.json         → nyaysetu-app/backend/config/jurisdiction_rules.json
├── index.html                      → nyaysetu-app/frontend/index.html
├── requirements.txt                → nyaysetu-app/requirements.txt
├── runtime.txt                     → nyaysetu-app/runtime.txt
├── .gitignore                      → nyaysetu-app/.gitignore
├── PROJECT_README.md               → nyaysetu-app/README.md
├── DEPLOYMENT_GUIDE.md             → nyaysetu-app/DEPLOYMENT_GUIDE.md
└── setup.sh                        → nyaysetu-app/setup.sh
```

#### 5. Create __init__.py Files

```bash
# These are empty files but required for Python modules
touch backend/__init__.py
touch backend/generators/__init__.py
touch backend/utils/__init__.py
```

## 📋 Complete Directory Tree

Your final structure should look like this:

```
nyaysetu-app/
│
├── backend/
│   ├── __init__.py                 (create empty file)
│   ├── app.py                      (from downloads)
│   │
│   ├── generators/
│   │   ├── __init__.py             (create empty file)
│   │   ├── rti_generator.py        (from downloads)
│   │   ├── affidavit_generator.py  (from downloads)
│   │   └── orchestrator.py         (from downloads)
│   │
│   ├── config/
│   │   └── jurisdiction_rules.json (from downloads)
│   │
│   ├── utils/
│   │   └── __init__.py             (create empty file)
│   │
│   └── outputs/                    (auto-created, for PDFs)
│
├── frontend/
│   ├── index.html                  (from downloads)
│   ├── css/                        (optional, for future CSS files)
│   ├── js/                         (optional, for future JS files)
│   └── assets/                     (optional, for images/icons)
│
├── requirements.txt                (from downloads)
├── runtime.txt                     (from downloads)
├── .gitignore                      (from downloads)
├── .env                            (create manually, see below)
├── README.md                       (from downloads - PROJECT_README.md)
├── DEPLOYMENT_GUIDE.md             (from downloads)
├── setup.sh                        (from downloads)
│
└── venv/                           (created by setup.sh)
```

## 🚀 Quick Setup Commands

### Option 1: Manual Setup

```bash
# 1. Create directories
mkdir nyaysetu-app
cd nyaysetu-app
mkdir -p backend/generators backend/config backend/outputs backend/utils
mkdir -p frontend/css frontend/js

# 2. Copy downloaded files to appropriate locations
# (Use your file manager or terminal)

# 3. Create __init__.py files
touch backend/__init__.py
touch backend/generators/__init__.py
touch backend/utils/__init__.py

# 4. Create .env file
cat > .env << 'EOF'
FLASK_APP=backend/app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-change-in-production
PORT=5000
EOF

# 5. Create virtual environment
python3 -m venv venv

# 6. Activate virtual environment
source venv/bin/activate  # Mac/Linux
# or
venv\Scripts\activate     # Windows

# 7. Install dependencies
pip install -r requirements.txt

# 8. Run backend
cd backend
python app.py
```

### Option 2: Using Setup Script

```bash
# 1. Create directories and place all files
# 2. Make setup script executable
chmod +x setup.sh

# 3. Run setup script
./setup.sh

# 4. Follow the instructions printed by the script
```

## 📝 File Descriptions

### Backend Files

| File | Purpose | Location |
|------|---------|----------|
| `app.py` | Main Flask API server | `backend/` |
| `rti_generator.py` | RTI document generator | `backend/generators/` |
| `affidavit_generator.py` | Affidavit generator | `backend/generators/` |
| `orchestrator.py` | AI requirement analyzer | `backend/generators/` |
| `jurisdiction_rules.json` | State-specific rules | `backend/config/` |
| `__init__.py` | Python package marker | `backend/`, `backend/generators/` |

### Frontend Files

| File | Purpose | Location |
|------|---------|----------|
| `index.html` | Main UI | `frontend/` |

### Configuration Files

| File | Purpose | Location |
|------|---------|----------|
| `requirements.txt` | Python dependencies | Root |
| `runtime.txt` | Python version for Render | Root |
| `.env` | Environment variables | Root |
| `.gitignore` | Git ignore rules | Root |

### Documentation Files

| File | Purpose | Location |
|------|---------|----------|
| `README.md` | Project overview | Root |
| `DEPLOYMENT_GUIDE.md` | Deployment instructions | Root |
| `setup.sh` | Quick setup script | Root |

## ✅ Verification Checklist

After organizing files, verify:

- [ ] All files are in correct directories
- [ ] `__init__.py` files exist in:
  - [ ] `backend/`
  - [ ] `backend/generators/`
  - [ ] `backend/utils/`
- [ ] `.env` file created (not in git)
- [ ] `requirements.txt` in root
- [ ] `jurisdiction_rules.json` in `backend/config/`
- [ ] `index.html` in `frontend/`

## 🔍 Common Issues & Solutions

### Issue: "No module named 'generators'"

**Solution**: Ensure `__init__.py` exists in `backend/generators/`

```bash
touch backend/generators/__init__.py
```

### Issue: "jurisdiction_rules.json not found"

**Solution**: Verify file is in `backend/config/` directory

```bash
ls backend/config/jurisdiction_rules.json
```

### Issue: "Cannot import app"

**Solution**: Ensure you're running from correct directory

```bash
# Should be in nyaysetu-app/backend/
cd backend
python app.py
```

### Issue: Frontend can't connect to backend

**Solution**: Update API_URL in `frontend/index.html`

```javascript
// For local development:
const API_URL = 'http://localhost:5000';

// For production (after deploying to Render):
const API_URL = 'https://your-app-name.onrender.com';
```

## 📱 Testing After Setup

### 1. Test Backend

```bash
# Activate venv
source venv/bin/activate

# Run backend
cd backend
python app.py

# In another terminal, test API
curl http://localhost:5000/
```

Expected output:
```json
{
  "status": "success",
  "message": "NyaySetu API v2.0",
  ...
}
```

### 2. Test Frontend

```bash
# Open another terminal
cd frontend
python3 -m http.server 8000

# Open browser
# http://localhost:8000
```

### 3. Test Full Flow

1. Open frontend in browser
2. Go to "AI Analysis" tab
3. Enter: "I need RTI for exam records"
4. Click "Analyze Requirement"
5. Should see complexity score and analysis

## 🌐 Deployment Preparation

### Before Deploying to Render:

1. **Test locally** - Ensure everything works
2. **Initialize git** - If not already done
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```
3. **Update frontend API_URL** - Point to your Render backend URL
4. **Push to GitHub**
   ```bash
   git remote add origin https://github.com/yourusername/nyaysetu-app.git
   git push -u origin main
   ```
5. **Follow DEPLOYMENT_GUIDE.md**

## 📊 File Size Reference

Approximate sizes:

```
app.py                      ~6KB
rti_generator.py            ~7KB
affidavit_generator.py      ~4KB
orchestrator.py             ~3KB
jurisdiction_rules.json     ~3KB
index.html                  ~18KB
requirements.txt            ~200B
runtime.txt                 ~15B
```

Total project size: ~50KB (excluding venv and generated PDFs)

## 🎯 Quick Commands Reference

```bash
# Setup
./setup.sh

# Run backend
source venv/bin/activate && cd backend && python app.py

# Run frontend
cd frontend && python3 -m http.server 8000

# Install new dependency
pip install package-name
pip freeze > requirements.txt

# Generate requirements from existing venv
pip freeze > requirements.txt

# Test API
curl http://localhost:5000/api/states

# Check Python packages
pip list
```

## 📞 Need Help?

1. Check `DEPLOYMENT_GUIDE.md` for detailed instructions
2. Verify all files are in correct locations (see checklist above)
3. Check logs for error messages
4. Ensure Python 3.8+ is installed
5. Ensure all dependencies are installed: `pip install -r requirements.txt`

---

**You're all set! Follow the verification checklist and testing steps above.** 🚀
