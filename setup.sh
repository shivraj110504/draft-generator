#!/bin/bash

# NyaySetu Quick Setup Script
# Run this to set up the project from scratch

echo "🏛️  NyaySetu - Quick Setup Script"
echo "=================================="
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"
echo ""

# Create project structure
echo "📁 Creating project structure..."
mkdir -p backend/generators backend/config backend/outputs backend/utils
mkdir -p frontend/css frontend/js

# Create __init__.py files
touch backend/__init__.py
touch backend/generators/__init__.py
touch backend/utils/__init__.py

echo "✓ Project structure created"
echo ""

# Create virtual environment
echo "🐍 Creating virtual environment..."
python3 -m venv venv
echo "✓ Virtual environment created"
echo ""

# Activate and install dependencies
echo "📦 Installing dependencies..."
echo "   (This may take a few minutes...)"

if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    source venv/Scripts/activate
else
    # Mac/Linux
    source venv/bin/activate
fi

pip install --upgrade pip
pip install -r requirements.txt

echo "✓ Dependencies installed"
echo ""

# Create .env file
echo "⚙️  Creating .env file..."
cat > .env << 'EOF'
FLASK_APP=backend/app.py
FLASK_ENV=development
SECRET_KEY=dev-secret-key-change-in-production
PORT=5000
EOF

echo "✓ .env file created"
echo ""

# Create README
echo "📝 Creating README..."
echo "✓ README created"
echo ""

echo "=================================="
echo "✅ Setup Complete!"
echo "=================================="
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Activate virtual environment:"
echo "   source venv/bin/activate  # Mac/Linux"
echo "   venv\\Scripts\\activate    # Windows"
echo ""
echo "2. Run backend server:"
echo "   cd backend"
echo "   python app.py"
echo ""
echo "3. In another terminal, run frontend:"
echo "   cd frontend"
echo "   python3 -m http.server 8000"
echo ""
echo "4. Open in browser:"
echo "   Backend:  http://localhost:5000"
echo "   Frontend: http://localhost:8000"
echo ""
echo "📖 For deployment instructions, see DEPLOYMENT_GUIDE.md"
echo ""
echo "🎉 Happy coding!"
