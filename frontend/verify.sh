#!/bin/bash

# Frontend Verification Script
# Checks that everything is set up correctly

set -e

echo "================================"
echo "SmartSalud Frontend Verification"
echo "================================"
echo ""

# Check Node.js version
echo "✓ Checking Node.js version..."
NODE_VERSION=$(node --version)
echo "  Node.js: $NODE_VERSION"

# Check npm version
echo "✓ Checking npm version..."
NPM_VERSION=$(npm --version)
echo "  npm: $NPM_VERSION"

# Check if node_modules exists
if [ -d "node_modules" ]; then
    echo "✓ Dependencies installed"
else
    echo "✗ Dependencies not installed"
    echo "  Run: npm install"
    exit 1
fi

# Check if backend is running
echo "✓ Checking backend..."
if curl -s http://localhost:8001/health > /dev/null 2>&1; then
    echo "  Backend is running on :8001"
else
    echo "  ⚠ Backend is NOT running"
    echo "  Start with: PYTHONPATH=\$PWD ../venv/bin/uvicorn src.api.main:app --reload --port 8001"
fi

# Verify key files exist
echo "✓ Checking project files..."
FILES=(
    "src/main.jsx"
    "src/App.jsx"
    "src/api/client.js"
    "src/components/layout/Layout.jsx"
    "src/components/layout/Sidebar.jsx"
    "src/components/layout/Header.jsx"
    "src/pages/Dashboard.jsx"
    "vite.config.js"
    "tailwind.config.js"
    "package.json"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ✗ $file (missing)"
        exit 1
    fi
done

echo ""
echo "================================"
echo "✅ All checks passed!"
echo "================================"
echo ""
echo "To start development:"
echo "  1. Ensure backend is running:"
echo "     cd /Users/autonomos_dev/Projects/smartSalud_V2"
echo "     PYTHONPATH=\$PWD ./venv/bin/uvicorn src.api.main:app --reload --port 8001"
echo ""
echo "  2. Start frontend:"
echo "     cd frontend"
echo "     npm run dev"
echo ""
echo "  3. Open: http://localhost:3000"
echo ""
