#!/usr/bin/env bash

# Exit on error
set -o errexit

echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo "🧠 Downloading model artifacts..."

REPO="sidnei-almeida/tmdb-semantic-recommender"
RELEASE_TAG="v0.0.1"
BASE_URL="https://github.com/${REPO}/releases/download/${RELEASE_TAG}"

echo "📥 Using release: ${RELEASE_TAG}"

# Create models directory
mkdir -p models

# Download Annoy index
echo "  → Downloading movies.ann..."
curl -L -f "${BASE_URL}/movies.ann" -o models/movies.ann

# Download movies map
echo "  → Downloading movies_map.pkl..."
curl -L -f "${BASE_URL}/movies_map.pkl" -o models/movies_map.pkl

# Download ONNX model
echo "  → Downloading model_quantized.zip..."
curl -L -f "${BASE_URL}/model_quantized.zip" -o models/model_quantized.zip

echo "🗄️ Extracting model..."
# Check if unzip is available, otherwise use Python
if command -v unzip &> /dev/null; then
  unzip -o models/model_quantized.zip -d models/model_quantized
else
  echo "  → unzip not found, using Python to extract..."
  python3 -c "import zipfile; zipfile.ZipFile('models/model_quantized.zip').extractall('models/model_quantized')"
fi

# Remove zip file after extraction
rm models/model_quantized.zip

# Verify extraction was successful
if [ ! -d "models/model_quantized" ] || [ ! -f "models/model_quantized/model_quantized.onnx" ]; then
  echo "❌ ERROR: Failed to extract model_quantized.zip!"
  exit 1
fi
echo "  → Model extracted successfully"

# Verify files exist
echo "✅ Verifying files..."
if [ ! -f "models/movies.ann" ] || [ ! -f "models/movies_map.pkl" ] || [ ! -f "models/model_quantized/model_quantized.onnx" ]; then
  echo "❌ ERROR: Some model files are missing!"
  exit 1
fi

echo "✅ Build completed successfully!"
