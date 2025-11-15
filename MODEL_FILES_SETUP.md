# 📦 Model Files Setup

Model files are too large to be versioned in Git. They are available as **GitHub Releases**.

## 📥 How to Download the Files

### Option 1: Manual Download

1. Visit the [Releases](https://github.com/sidnei-almeida/tmdb-semantic-recommender/releases/tag/v0.0.1) page
2. Download the following files:
   - `model_quantized.zip` - Quantized ONNX model and tokenizer (17.4 MB)
   - `movies.ann` - Annoy index (132 MB)
   - `movies_map.pkl` - ID mapping (6.3 MB)

### Integrity Verification (SHA256)

To verify the integrity of downloaded files:

```bash
# model_quantized.zip
echo "41a8bed8cf1068936db539fcbee8f590f83b5a4f822300d9abc0332704f4919d  model_quantized.zip" | sha256sum -c

# movies.ann
echo "c7cade5c98ab0b8117feea3831100c60c5b3b66b7a292d82548001c0092b0ce7  movies.ann" | sha256sum -c

# movies_map.pkl
echo "7a577e02b47b8c224ed9677bfe53e71078462c76456eeffb2b9fd43d5cbf97fa  movies_map.pkl" | sha256sum -c
```

3. Extract/place the files in the correct structure:
   ```
   models/
   ├── model_quantized/
   │   ├── model_quantized.onnx
   │   ├── tokenizer.json
   │   └── ... (other model files)
   ├── movies.ann
   └── movies_map.pkl
   ```

### Option 2: Automated Download Script (Bash)

Create a script `download_models.sh`:

```bash
#!/bin/bash

REPO="sidnei-almeida/tmdb-semantic-recommender"
RELEASE_TAG="v0.0.1"  # Or use "latest" to get the latest release

echo "Downloading files from release ${RELEASE_TAG}..."

# Create models directory if it doesn't exist
mkdir -p models

# Download model_quantized.zip
echo "Downloading model_quantized.zip..."
curl -L "https://github.com/${REPO}/releases/download/${RELEASE_TAG}/model_quantized.zip" -o models/model_quantized.zip

# Extract model_quantized.zip
echo "Extracting model_quantized.zip..."
unzip -q models/model_quantized.zip -d models/
rm models/model_quantized.zip

# Download movies.ann
echo "Downloading movies.ann..."
curl -L "https://github.com/${REPO}/releases/download/${RELEASE_TAG}/movies.ann" -o models/movies.ann

# Download movies_map.pkl
echo "Downloading movies_map.pkl..."
curl -L "https://github.com/${REPO}/releases/download/${RELEASE_TAG}/movies_map.pkl" -o models/movies_map.pkl

# Verify integrity (optional)
echo "Verifying file integrity..."
echo "c7cade5c98ab0b8117feea3831100c60c5b3b66b7a292d82548001c0092b0ce7  models/movies.ann" | sha256sum -c
echo "7a577e02b47b8c224ed9677bfe53e71078462c76456eeffb2b9fd43d5cbf97fa  models/movies_map.pkl" | sha256sum -c

echo "✅ All files downloaded successfully!"
```

Make the script executable and run:
```bash
chmod +x download_models.sh
./download_models.sh
```

### Option 3: Python Script

Create a script `download_models.py`:

```python
#!/usr/bin/env python3
"""
Script to download model files from GitHub Releases.
"""
import os
import requests
import zipfile
from pathlib import Path

REPO = "sidnei-almeida/tmdb-semantic-recommender"
RELEASE_TAG = "v0.0.1"  # Or "latest" to get the latest release
MODELS_DIR = Path("models")

def get_release_tag():
    """Gets the release tag (or uses the specified one)."""
    if RELEASE_TAG == "latest":
        url = f"https://api.github.com/repos/{REPO}/releases/latest"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()["tag_name"]
    return RELEASE_TAG

def download_file(url: str, dest: Path):
    """Downloads a file from URL to destination."""
    print(f"Downloading {dest.name}...")
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    dest.parent.mkdir(parents=True, exist_ok=True)
    
    with open(dest, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"✅ {dest.name} downloaded!")

def main():
    print(f"Using release: {RELEASE_TAG}")
    tag = get_release_tag()
    print(f"Release: {tag}\n")
    
    base_url = f"https://github.com/{REPO}/releases/download/{tag}"
    
    # Download and extract model_quantized.zip
    zip_path = MODELS_DIR / "model_quantized.zip"
    download_file(f"{base_url}/model_quantized.zip", zip_path)
    
    print("Extracting model_quantized.zip...")
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(MODELS_DIR)
    zip_path.unlink()
    print("✅ Model extracted!\n")
    
    # Download movies.ann
    download_file(f"{base_url}/movies.ann", MODELS_DIR / "movies.ann")
    
    # Download movies_map.pkl
    download_file(f"{base_url}/movies_map.pkl", MODELS_DIR / "movies_map.pkl")
    
    print("\n✅ All files downloaded successfully!")
    print(f"Files in: {MODELS_DIR.absolute()}")

if __name__ == "__main__":
    main()
```

Run:
```bash
python3 download_models.py
```

## 📋 Expected Final Structure

After downloading, the structure should be:

```
models/
├── model_quantized/
│   ├── model_quantized.onnx
│   ├── tokenizer.json
│   ├── tokenizer_config.json
│   ├── config.json
│   ├── vocab.txt
│   └── ... (other files)
├── movies.ann          (132MB)
└── movies_map.pkl      (6.3MB)
```

## ⚠️ Important

- **Do NOT commit** these files to Git (they are in `.gitignore`)
- Files are required for the API to work
- Make sure you have enough disk space (~156MB)

## 🔗 Useful Links

- [GitHub Releases - v0.0.1](https://github.com/sidnei-almeida/tmdb-semantic-recommender/releases/tag/v0.0.1)
- [All Releases](https://github.com/sidnei-almeida/tmdb-semantic-recommender/releases)
- [API Documentation](README.md)

## 📝 Notes

- **Current release**: v0.0.1 (62K movies model)
- **Total size**: ~156 MB
- Files are required for the API to work correctly
