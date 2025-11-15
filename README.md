<div align="center">

# 🎬 TMDB Semantic Recommender API

**High-Performance Movie Recommendation API based on Content Similarity using Deep Learning (BERT/ONNX) and Vector Search**

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg)](https://fastapi.tiangolo.com/)
[![ONNX Runtime](https://img.shields.io/badge/ONNX%20Runtime-1.22.1-005CED.svg)](https://onnxruntime.ai/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

[Features](#-features) • [Quick Start](#-quick-start) • [API Documentation](#-api-documentation) • [Deployment](#-deployment) • [Contributing](#-contributing)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
- [API Documentation](#-api-documentation)
- [Local Development](#-local-development)
- [Deployment](#-deployment)
- [Performance](#-performance)
- [Technology Stack](#-technology-stack)
- [Project Structure](#-project-structure)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

The **TMDB Semantic Recommender API** is a production-ready REST API that provides intelligent movie recommendations based on semantic similarity of movie synopses. Built with state-of-the-art deep learning techniques, it leverages the **all-MiniLM-L6-v2** model (quantized to INT8) in ONNX format for efficient embedding generation and an Annoy index for lightning-fast similarity search across **30,000 movies**.

### Key Innovation: Context-Aware Metadata Enrichment

Unlike traditional synopsis-only approaches, our model uses **context-enriched embeddings** by including genre, year, and title alongside the synopsis:

```
"Genre: Horror. Year: 2018. Title: Hereditary. Overview: ..."
```

This creates **semantic anchors** that prevent context confusion (e.g., "family" in Horror ≠ "family" in Romance), resulting in dramatically more accurate recommendations.

### Key Highlights

- ⚡ **Lightning Fast**: Optimized for low-latency inference (~50-100ms per request)
- 🧠 **AI-Powered**: Uses quantized BERT embeddings for semantic understanding
- 📦 **Production Ready**: Fully configured for seamless deployment on Render
- 💾 **Memory Efficient**: Optimized to run within 512MB RAM constraints
- 🔍 **Vector Search**: Fast approximate nearest neighbor search with Annoy
- 📚 **Auto Documentation**: Interactive API docs with Swagger UI

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **🎯 Semantic Search** | Uses all-MiniLM-L6-v2 model (quantized INT8) with context-aware metadata enrichment |
| **⚡ Fast Vector Search** | Annoy index with 30k movies for efficient similarity search (sub-millisecond query times) |
| **🧠 Context Awareness** | Genre/Year/Title anchors prevent semantic confusion across different movie universes |
| **🚀 RESTful API** | Built with FastAPI for high performance and automatic OpenAPI documentation |
| **🔄 Async Support** | Full async/await support for handling concurrent requests efficiently |
| **💾 Memory Optimized** | Configured to run within Render's free tier (512MB RAM) |
| **📊 Health Monitoring** | Built-in health check endpoints for service monitoring |
| **🔒 Type Safe** | Full type hints with Pydantic validation |

---

## 🏗️ Architecture

```
┌─────────────┐
│   Client    │
│  (Frontend) │
└──────┬──────┘
       │ HTTP POST
       │ /api/v1/recommend
       ▼
┌─────────────────────────────────────┐
│        FastAPI Application          │
│  ┌──────────────────────────────┐   │
│  │   API Route Handler          │   │
│  └───────────┬──────────────────┘   │
│              │                       │
│              ▼                       │
│  ┌──────────────────────────────┐   │
│  │    Model Service             │   │
│  │  ┌────────────────────────┐  │   │
│  │  │  BERT Tokenizer        │  │   │
│  │  └──────────┬─────────────┘  │   │
│  │             ▼                │   │
│  │  ┌────────────────────────┐  │   │
│  │  │  ONNX Runtime          │  │   │
│  │  │  (Embedding Gen)       │  │   │
│  │  └──────────┬─────────────┘  │   │
│  │             ▼                │   │
│  │  ┌────────────────────────┐  │   │
│  │  │  Annoy Index Search    │  │   │
│  │  └──────────┬─────────────┘  │   │
│  └─────────────┼────────────────┘   │
└────────────────┼────────────────────┘
                 │
                 ▼
         ┌───────────────┐
         │ Recommendations│
         │  (Movie IDs)   │
         └───────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11** (recommended) or 3.10+
- `pip` package manager
- Virtual environment (recommended)

### Installation

```bash
# Clone the repository
git clone https://github.com/sidnei-almeida/tmdb-semantic-recommender.git
cd tmdb-semantic-recommender

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Download model files from GitHub Releases
# See MODEL_FILES_SETUP.md for detailed instructions
# Quick download:
# wget https://github.com/sidnei-almeida/tmdb-semantic-recommender/releases/download/v0.0.1/model_quantized.zip
# wget https://github.com/sidnei-almeida/tmdb-semantic-recommender/releases/download/v0.0.1/movies.ann
# wget https://github.com/sidnei-almeida/tmdb-semantic-recommender/releases/download/v0.0.1/movies_map.pkl
# unzip model_quantized.zip -d models/
# mv movies.ann models/
# mv movies_map.pkl models/

# Run the application
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**⚠️ Important**: Before running the API, you need to download the model files from [GitHub Releases](https://github.com/sidnei-almeida/tmdb-semantic-recommender/releases/tag/v0.0.1). See [MODEL_FILES_SETUP.md](MODEL_FILES_SETUP.md) for detailed instructions.

The API will be available at `http://localhost:8000`

📖 **Interactive API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 📚 API Documentation

### Base URL

```
Production: https://tmdb-semantic-recommender.onrender.com
Local:      http://localhost:8000
```

### Endpoints

#### `POST /api/v1/recommend`

Get movie recommendations based on synopsis similarity.

**Request**

```bash
curl -X POST "http://localhost:8000/api/v1/recommend" \
  -H "Content-Type: application/json" \
  -d '{
    "synopsis": "A young wizard discovers his magical heritage and must face the dark lord who killed his parents.",
    "top_k": 10
  }'
```

**Request Body**

```json
{
  "synopsis": "string (required, 10-5000 characters)",
  "top_k": "integer (optional, 1-50, default: 10)"
}
```

**Response**

```json
{
  "query": "A young wizard discovers...",
  "recommendations": [
    {
      "movie_id": 12345,
      "similarity_score": 0.95,
      "title": "Harry Potter and the Philosopher's Stone",
      "overview": "A young wizard's journey..."
    }
  ],
  "count": 10
}
```

#### `GET /health`

Health check endpoint to verify service status and model loading.

**Response**

```json
{
  "status": "healthy",
  "model_loaded": true
}
```

#### `GET /`

Root endpoint with API information.

#### `GET /docs`

Interactive API documentation (Swagger UI).

#### `GET /redoc`

Alternative API documentation (ReDoc).

---

## 💻 Local Development

### Quick Start Script

```bash
# Make executable
chmod +x run_local.sh

# Run (creates venv, installs deps, starts server)
./run_local.sh
```

### Manual Setup

<details>
<summary>Click to expand detailed setup instructions</summary>

#### 1. Clone Repository

```bash
git clone https://github.com/sidnei-almeida/tmdb-semantic-recommender.git
cd tmdb-semantic-recommender
```

#### 2. Create Virtual Environment

```bash
# Linux/Mac
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

#### 3. Install Dependencies

```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

**Note**: If `tokenizers` is compiling slowly:
```bash
# Install tokenizers with binary preference
pip install tokenizers --prefer-binary
pip install -r requirements.txt
```

#### 4. Run Application

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

</details>

### Testing

#### Using cURL

```bash
# Health check
curl http://localhost:8000/health

# Get recommendations
curl -X POST "http://localhost:8000/api/v1/recommend" \
  -H "Content-Type: application/json" \
  -d '{
    "synopsis": "A space opera about rebels fighting an empire",
    "top_k": 5
  }'
```

#### Using Python

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/recommend",
    json={
        "synopsis": "A young wizard discovers his magical heritage",
        "top_k": 10
    }
)

data = response.json()
for movie in data["recommendations"]:
    print(f"Movie ID: {movie['movie_id']}")
    print(f"Similarity: {movie['similarity_score']:.2%}")
    print(f"Title: {movie.get('title', 'N/A')}")
    print("---")
```

### Troubleshooting

<details>
<summary>Common Issues and Solutions</summary>

#### Model Files Not Found

Ensure all model files are present:
- `models/model_quantized/model_quantized.onnx`
- `models/model_quantized/tokenizer.json`
- `models/model_quantized/config.json`
- `models/movies.ann`
- `models/movies_map.pkl`

#### Port Already in Use

```bash
# Use a different port
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

#### Dependency Installation Issues

- Use Python 3.11 (recommended) or 3.10+
- Python 3.13+ may require compilation for some packages
- Update pip: `pip install --upgrade pip setuptools wheel`

#### Tokenizers Compilation (Python 3.13+)

- **Option 1**: Install Python 3.11 and create new venv
- **Option 2**: Install Rust: `sudo pacman -S rust` (speeds up compilation)
- **Option 3**: Wait for compilation (5-10 minutes)

</details>

---

## 🚢 Deployment

### Deploy to Render

#### Option 1: Using Render Dashboard

1. Create a new **Web Service** on [Render](https://render.com)
2. Connect your GitHub repository
3. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Environment**: `Python 3`
   - **Python Version**: `3.11.0`

4. The `render.yaml` file provides automatic configuration

#### Option 2: Using Render CLI

```bash
# Install Render CLI
npm install -g render-cli

# Login
render login

# Deploy
render deploy
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Server port | Auto-set by Render |
| `DEBUG` | Debug mode | `false` |

### Memory Optimization (512MB Limit)

This API is optimized for Render's free tier:

**Optimizations Applied:**
- ✅ CPU Memory Arena disabled (~30-50MB saved)
- ✅ Memory pattern optimization disabled
- ✅ Sequential execution mode
- ✅ Basic graph optimization level

**Memory Breakdown:**
```
Model (ONNX - all-MiniLM-L6-v2):  ~50-100MB
Annoy Index (30k movies):          ~30-60MB
Python + FastAPI:                  ~50-100MB
Libraries Overhead:                ~50-100MB
Working Memory:                    ~50-100MB
─────────────────────────────────────────────────
Total Estimated:                   ~330-460MB ✅
```

---

## ⚡ Performance

| Metric | Value |
|--------|-------|
| **Model Loading** | 2-5 seconds (startup) |
| **Inference Time** | 50-100ms per request |
| **Concurrent Requests** | Supported (async/await) |
| **Memory Usage** | ~300-450MB (optimized) |
| **API Latency** | <100ms (p95) |

---

## 🛠️ Technology Stack

| Technology | Purpose | Version |
|------------|---------|---------|
| [FastAPI](https://fastapi.tiangolo.com/) | Web framework | 0.115.0 |
| [ONNX Runtime](https://onnxruntime.ai/) | Model inference | 1.22.1 |
| [all-MiniLM-L6-v2](https://www.sbert.net/docs/pretrained_models.html) | Sentence embeddings (quantized) | Latest |
| [Annoy](https://github.com/spotify/annoy) | Vector similarity search (30k movies) | 1.17.3 |
| [Tokenizers](https://github.com/huggingface/tokenizers) | Text tokenization | ≥0.20.0 |
| [NumPy](https://numpy.org/) | Numerical computing | 1.26.4 |
| [Pydantic](https://docs.pydantic.dev/) | Data validation | 2.9.2 |
| [Uvicorn](https://www.uvicorn.org/) | ASGI server | 0.31.0 |

---

## 📁 Project Structure

```
tmdb-semantic-recommender/
│
├── app/                          # Application package
│   ├── __init__.py
│   ├── main.py                   # FastAPI app & lifespan
│   │
│   ├── api/                      # API routes
│   │   ├── __init__.py
│   │   └── routes.py             # Endpoint definitions
│   │
│   ├── core/                     # Core configuration
│   │   ├── __init__.py
│   │   └── config.py             # Settings & environment
│   │
│   └── services/                 # Business logic
│       ├── __init__.py
│       └── model_service.py      # Model loading & inference
│
├── models/                       # Model files
│   ├── model_quantized/          # all-MiniLM-L6-v2 ONNX model (quantized)
│   │   ├── model_quantized.onnx
│   │   ├── tokenizer.json
│   │   └── config.json
│   ├── movies.ann                # Annoy index (30k movies)
│   └── movies_map.pkl            # Movie ID mapping (Annoy ID → TMDB data)
│
├── requirements.txt              # Python dependencies
├── render.yaml                   # Render deployment config
├── runtime.txt                   # Python version
├── run_local.sh                  # Local setup script
├── .gitignore
└── README.md                     # This file
```

---

## 📖 Usage Examples

### Python Client

```python
import requests

# Get recommendations
response = requests.post(
    "https://tmdb-semantic-recommender.onrender.com/api/v1/recommend",
    json={
        "synopsis": "A space opera about rebels fighting an empire",
        "top_k": 10
    }
)

data = response.json()
for movie in data["recommendations"]:
    print(f"ID: {movie['movie_id']} | Score: {movie['similarity_score']:.2%}")
```

### JavaScript/TypeScript Client

```javascript
const response = await fetch('https://tmdb-semantic-recommender.onrender.com/api/v1/recommend', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    synopsis: selectedMovieOverview,
    top_k: 10
  })
});

const { recommendations } = await response.json();

// Fetch full details from TMDB
for (const rec of recommendations) {
  const tmdbResponse = await fetch(
    `https://api.themoviedb.org/3/movie/${rec.movie_id}?api_key=YOUR_TMDB_API_KEY`
  );
  const movieDetails = await tmdbResponse.json();
  // Display in UI
}
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**sidnei-almeida**

- GitHub: [@sidnei-almeida](https://github.com/sidnei-almeida)
- Project Link: [https://github.com/sidnei-almeida/tmdb-semantic-recommender](https://github.com/sidnei-almeida/tmdb-semantic-recommender)

---

<div align="center">

**Made with ❤️ using FastAPI and ONNX Runtime**

[⭐ Star this repo](https://github.com/sidnei-almeida/tmdb-semantic-recommender) if you find it helpful!

</div>
