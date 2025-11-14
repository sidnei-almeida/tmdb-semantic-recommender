#!/bin/bash
# Script to run the API locally

echo "🚀 Starting TMDB Semantic Recommender API locally..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Run the application
echo "🎬 Starting server..."
echo "📍 API will be available at: http://localhost:8000"
echo "📚 Documentation at: http://localhost:8000/docs"
echo ""
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

