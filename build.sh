#!/bin/bash
set -e  # Exit on error

echo "🚀 Starting build process..."
echo "📂 Current directory: $(pwd)"
echo "📂 Script location: ${BASH_SOURCE[0]}"
echo "📂 Working directory: $(pwd)"

# Check if unzip is available (required for extracting model files)
if ! command -v unzip &> /dev/null; then
  echo "⚠️  unzip not found, using Python zipfile module instead..."
  USE_PYTHON_UNZIP=true
else
  USE_PYTHON_UNZIP=false
fi

# Download model files from GitHub Releases
echo "📥 Downloading model files from GitHub Releases..."

REPO="sidnei-almeida/tmdb-semantic-recommender"
# Use "latest" by default, or allow override via environment variable
RELEASE_TAG="${MODEL_RELEASE_TAG:-latest}"
MODELS_DIR="models"

# Fetch the latest release tag from GitHub API
echo "  → Fetching latest release tag from GitHub API..."
RELEASE_TAG=$(curl -s "https://api.github.com/repos/${REPO}/releases/latest" | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/')
if [ -z "$RELEASE_TAG" ]; then
  echo "❌ Failed to fetch latest release tag from GitHub API"
  echo "   Falling back to v0.0.1..."
  RELEASE_TAG="v0.0.1"
fi
echo "  → Repository: ${REPO}"
echo "  → Release: ${RELEASE_TAG}"

# Create models directory if it doesn't exist
mkdir -p "${MODELS_DIR}"
echo "  → Created/verified models directory: $(pwd)/${MODELS_DIR}"

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
echo "     URL: https://github.com/${REPO}/releases/download/${RELEASE_TAG}/movies.ann"
curl -L -f --progress-bar "https://github.com/${REPO}/releases/download/${RELEASE_TAG}/movies.ann" \
  -o "${MODELS_DIR}/movies.ann" || {
  echo "❌ Failed to download movies.ann"
  echo "   Check if the release ${RELEASE_TAG} exists and contains movies.ann"
  exit 1
}
echo "  → movies.ann downloaded successfully"

# Download movies_map.pkl
echo "  → Downloading movies_map.pkl..."
echo "     URL: https://github.com/${REPO}/releases/download/${RELEASE_TAG}/movies_map.pkl"
curl -L -f --progress-bar "https://github.com/${REPO}/releases/download/${RELEASE_TAG}/movies_map.pkl" \
  -o "${MODELS_DIR}/movies_map.pkl" || {
  echo "❌ Failed to download movies_map.pkl"
  echo "   Check if the release ${RELEASE_TAG} exists and contains movies_map.pkl"
  exit 1
}
echo "  → movies_map.pkl downloaded successfully"

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

# List files for debugging
echo "📋 Files in ${MODELS_DIR}:"
ls -lh "${MODELS_DIR}" || true
echo "📋 Files in ${MODELS_DIR}/model_quantized:"
ls -lh "${MODELS_DIR}/model_quantized" || true

# Verify file sizes
echo "📊 File sizes:"
if [ -f "${MODELS_DIR}/movies.ann" ]; then
  echo "  movies.ann: $(du -h ${MODELS_DIR}/movies.ann | cut -f1)"
fi
if [ -f "${MODELS_DIR}/movies_map.pkl" ]; then
  echo "  movies_map.pkl: $(du -h ${MODELS_DIR}/movies_map.pkl | cut -f1)"
fi
if [ -f "${MODELS_DIR}/model_quantized/model_quantized.onnx" ]; then
  echo "  model_quantized.onnx: $(du -h ${MODELS_DIR}/model_quantized/model_quantized.onnx | cut -f1)"
fi

# Final verification - ensure files will be available at runtime
echo "🔍 Final verification before build completion..."
if [ ! -f "${MODELS_DIR}/movies.ann" ] || [ ! -f "${MODELS_DIR}/movies_map.pkl" ] || [ ! -f "${MODELS_DIR}/model_quantized/model_quantized.onnx" ]; then
  echo "❌ CRITICAL: Some model files are missing after download!"
  echo "   This will cause the application to fail on startup."
  exit 1
fi

# Create a marker file to verify build completed
echo "v${RELEASE_TAG}" > "${MODELS_DIR}/.build_version"
echo "✅ Build marker created: ${MODELS_DIR}/.build_version"

echo "✅ Build verification passed!"
echo "📊 Build completed!"
echo ""
echo "📦 Summary:"
echo "   - Model files downloaded from release: ${RELEASE_TAG}"
echo "   - Files location: $(pwd)/${MODELS_DIR}/"
echo "   - Ready for application startup"

