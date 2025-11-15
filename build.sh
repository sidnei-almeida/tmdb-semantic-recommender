#!/bin/bash
set -e  # Exit on error

echo "🚀 Starting build process..."

# Check if unzip is available (required for extracting model files)
if ! command -v unzip &> /dev/null; then
  echo "⚠️  unzip not found, using Python zipfile module instead..."
  USE_PYTHON_UNZIP=true
else
  USE_PYTHON_UNZIP=false
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Download model files from GitHub Releases
echo "📥 Downloading model files from GitHub Releases..."

REPO="sidnei-almeida/tmdb-semantic-recommender"
RELEASE_TAG="v0.0.1"
MODELS_DIR="models"

# Create models directory if it doesn't exist
mkdir -p "${MODELS_DIR}"

# Download model_quantized.zip
echo "  → Downloading model_quantized.zip..."
curl -L -f "https://github.com/${REPO}/releases/download/${RELEASE_TAG}/model_quantized.zip" \
  -o "${MODELS_DIR}/model_quantized.zip" || {
  echo "❌ Failed to download model_quantized.zip"
  exit 1
}

# Extract model_quantized.zip
echo "  → Extracting model_quantized.zip..."
if [ "$USE_PYTHON_UNZIP" = true ]; then
  python3 -c "import zipfile; zipfile.ZipFile('${MODELS_DIR}/model_quantized.zip').extractall('${MODELS_DIR}/')" || {
    echo "❌ Failed to extract model_quantized.zip"
    exit 1
  }
else
  unzip -q "${MODELS_DIR}/model_quantized.zip" -d "${MODELS_DIR}/" || {
    echo "❌ Failed to extract model_quantized.zip"
    exit 1
  }
fi
rm "${MODELS_DIR}/model_quantized.zip"

# Download movies.ann
echo "  → Downloading movies.ann (132 MB)..."
curl -L -f "https://github.com/${REPO}/releases/download/${RELEASE_TAG}/movies.ann" \
  -o "${MODELS_DIR}/movies.ann" || {
  echo "❌ Failed to download movies.ann"
  exit 1
}

# Download movies_map.pkl
echo "  → Downloading movies_map.pkl..."
curl -L -f "https://github.com/${REPO}/releases/download/${RELEASE_TAG}/movies_map.pkl" \
  -o "${MODELS_DIR}/movies_map.pkl" || {
  echo "❌ Failed to download movies_map.pkl"
  exit 1
}

# Verify files exist
echo "✅ Verifying downloaded files..."
if [ ! -f "${MODELS_DIR}/movies.ann" ]; then
  echo "❌ movies.ann not found"
  exit 1
fi

if [ ! -f "${MODELS_DIR}/movies_map.pkl" ]; then
  echo "❌ movies_map.pkl not found"
  exit 1
fi

if [ ! -f "${MODELS_DIR}/model_quantized/model_quantized.onnx" ]; then
  echo "❌ model_quantized.onnx not found"
  exit 1
fi

if [ ! -f "${MODELS_DIR}/model_quantized/tokenizer.json" ]; then
  echo "❌ tokenizer.json not found"
  exit 1
fi

echo "✅ All model files downloaded and verified successfully!"
echo "📊 Build completed!"

