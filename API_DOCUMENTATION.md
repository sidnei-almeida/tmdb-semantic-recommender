# 📚 API Documentation - Frontend Integration Guide

**TMDB Semantic Recommender API**

Complete endpoint documentation for frontend integration.

## 🚀 What's New (Model Upgrade)

Our recommendation engine has been significantly improved:

- **🧠 Context-Aware Intelligence**: The model now uses **context-enriched embeddings** that include genre, year, and title alongside the synopsis. This prevents semantic confusion (e.g., "family" in Horror ≠ "family" in Romance).

- **📚 Expanded Library**: Increased from **10k to 30k movies** (300% more coverage), giving you a much better chance of finding the perfect recommendation.

- **⚡ Better Accuracy**: The model understands context, so searching for "Hereditary" (Horror, 2018) won't accidentally recommend romantic family movies—it will find actual horror films with similar themes.

**How it works internally**: The model processes text in the format:
```
"Genre: {genres}. Year: {year}. Title: {title}. Overview: {overview}"
```

This creates semantic anchors that dramatically improve recommendation quality.

---

## 🌐 Base URLs

| Environment | URL |
|------------|-----|
| **Production** | `https://tmdb-semantic-recommender.onrender.com` |
| **Local Development** | `http://localhost:8000` |
| **Interactive Docs** | `https://tmdb-semantic-recommender.onrender.com/docs` |

---

## 🔐 Authentication

**No authentication required** - All endpoints are publicly accessible.

**CORS**: Configured to allow requests from all origins.

---

## 📡 Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API information |
| `GET` | `/health` | Health check |
| `POST` | `/api/v1/recommend` | Get movie recommendations |

---

## 🔍 Endpoint Details

### 1. Get API Information

**Endpoint:** `GET /`

**Description:** Returns basic API information and status.

**Request:**
```http
GET / HTTP/1.1
Host: tmdb-semantic-recommender.onrender.com
```

**Response:**
```json
{
  "message": "TMDB Semantic Recommender API",
  "version": "1.0.0",
  "status": "running",
  "docs": "/docs"
}
```

**Status Codes:**
- `200 OK` - Success

---

### 2. Health Check

**Endpoint:** `GET /health`

**Description:** Checks if the API is running and the model is loaded.

**Request:**
```http
GET /health HTTP/1.1
Host: tmdb-semantic-recommender.onrender.com
```

**Response (Success):**
```json
{
  "status": "healthy",
  "model_loaded": true
}
```

**Response (Model Not Loaded):**
```json
{
  "detail": "Model not loaded"
}
```

**Status Codes:**
- `200 OK` - Service healthy and model loaded
- `503 Service Unavailable` - Model not loaded

**Usage:** Check this endpoint before making recommendation requests to ensure the service is ready.

---

### 3. Get Movie Recommendations ⭐

**Endpoint:** `POST /api/v1/recommend`

**Description:** Get movie recommendations based on synopsis similarity using **context-aware semantic embeddings**. 

**Model Details:**
- Uses **all-MiniLM-L6-v2** model (quantized to INT8 for efficiency)
- Processes **context-enriched metadata**: `"Genre: {genres}. Year: {year}. Title: {title}. Overview: {overview}"`
- Searches across **30,000 movies** (expanded from 10k)
- Results are ranked by cosine similarity (0.0 to 1.0)

**Why this is better:**
- **Context-aware**: Prevents genre confusion (e.g., "family" in Horror ≠ Romance)
- **Larger library**: 300% more movies means better matches
- **Higher quality**: Recommendations are more thematically consistent

**Request:**

```http
POST /api/v1/recommend HTTP/1.1
Host: tmdb-semantic-recommender.onrender.com
Content-Type: application/json

{
  "synopsis": "When Ellen, the matriarch of the Graham family, passes away, her daughter's family begins to unravel cryptic and increasingly terrifying secrets about their ancestry.",
  "genre": "Horror, Mystery, Thriller",
  "year": 2018,
  "title": "Hereditary",
  "top_k": 10
}
```

**Request Body Schema:**

```typescript
interface RecommendationRequest {
  synopsis: string;      // Required, 10-5000 characters
  genre?: string;        // Optional, movie genre(s) for context-aware recommendations
  year?: number;         // Optional, release year (1888-2100)
  title?: string;        // Optional, movie title (max 200 characters)
  top_k?: number;        // Optional, 1-50, default: 10
}
```

**Field Validation:**
- `synopsis`: 
  - **Required**: Yes
  - **Type**: `string`
  - **Min Length**: 10 characters
  - **Max Length**: 5000 characters
  - **Description**: Movie synopsis/overview
- `genre`:
  - **Required**: No (but recommended for better accuracy)
  - **Type**: `string`
  - **Description**: Movie genre(s) separated by commas (e.g., "Horror, Mystery, Thriller")
  - **Example**: "Horror, Mystery, Thriller"
- `year`:
  - **Required**: No (but recommended for better accuracy)
  - **Type**: `integer`
  - **Min**: 1888
  - **Max**: 2100
  - **Description**: Release year of the movie
- `title`:
  - **Required**: No (but recommended for better accuracy)
  - **Type**: `string`
  - **Max Length**: 200 characters
  - **Description**: Movie title
- `top_k`:
  - **Required**: No
  - **Type**: `integer`
  - **Default**: `10`
  - **Min**: `1`
  - **Max**: `50`

**Response (Success):**

**With metadata (recommended):**
```json
{
  "query": "Genre: Horror, Mystery, Thriller. Year: 2018. Title: Hereditary. Overview: When Ellen, the matriarch of the Graham family, passes away...",
  "recommendations": [
    {
      "movie_id": 2964,
      "similarity_score": 0.75,
      "title": "Hereditary",
      "overview": null
    },
    {
      "movie_id": 5739,
      "similarity_score": 0.72,
      "title": "A Tale of Two Sisters",
      "overview": null
    }
  ],
  "count": 10
}
```

**Without metadata (works, but less accurate):**
```json
{
  "query": "When Ellen, the matriarch of the Graham family, passes away...",
  "recommendations": [
    {
      "movie_id": 4825,
      "similarity_score": 0.66,
      "title": "The Vanished",
      "overview": null
    }
  ],
  "count": 10
}
```

**Response Schema:**

```typescript
interface RecommendationResponse {
  query: string;                    // Original query (enriched if metadata provided)
  recommendations: MovieRecommendation[];
  count: number;                    // Number of recommendations returned
}

interface MovieRecommendation {
  movie_id: number;                 // TMDB movie ID (use with TMDB API)
  similarity_score: number;         // Similarity score (0.0 to 1.0)
  title: string | null;             // Movie title (if available in mapping)
  overview: string | null;          // Movie overview (if available in mapping)
}
```

**Status Codes:**

| Code | Description |
|------|-------------|
| `200 OK` | Success - Recommendations returned |
| `400 Bad Request` | Invalid request (validation error) |
| `500 Internal Server Error` | Server error processing request |
| `503 Service Unavailable` | Model service not available |

**Error Response:**

```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## 💻 Frontend Integration Examples

### JavaScript / TypeScript

#### Basic Recommendation Request

```typescript
interface RecommendationRequest {
  synopsis: string;      // Required
  genre?: string;        // Optional (recommended)
  year?: number;         // Optional (recommended)
  title?: string;        // Optional (recommended)
  top_k?: number;        // Optional, default: 10
}

interface MovieRecommendation {
  movie_id: number;
  similarity_score: number;
  title: string | null;
  overview: string | null;
}

interface RecommendationResponse {
  query: string;                    // Shows enriched query if metadata provided
  recommendations: MovieRecommendation[];
  count: number;
}

const API_BASE_URL = 'https://tmdb-semantic-recommender.onrender.com';

async function getRecommendations(
  synopsis: string,
  genre?: string,
  year?: number,
  title?: string,
  topK: number = 10
): Promise<RecommendationResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/recommend`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      synopsis: synopsis,
      genre: genre,
      year: year,
      title: title,
      top_k: topK,
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || `HTTP error! status: ${response.status}`);
  }

  return await response.json();
}

// Usage - With metadata (recommended for better accuracy)
try {
  const result = await getRecommendations(
    "When Ellen, the matriarch of the Graham family, passes away, her daughter's family begins to unravel cryptic and increasingly terrifying secrets about their ancestry.",
    "Horror, Mystery, Thriller",  // genre
    2018,                          // year
    "Hereditary",                  // title
    10
  );
  
  console.log(`Found ${result.count} recommendations`);
  console.log(`Query used: ${result.query}`);
  result.recommendations.forEach(movie => {
    console.log(`${movie.movie_id}: ${movie.similarity_score.toFixed(2)} - ${movie.title}`);
  });
} catch (error) {
  console.error('Error:', error);
}

// Usage - Without metadata (works, but less accurate)
const result = await getRecommendations(
  "A space opera about rebels fighting an evil empire",
  undefined,  // genre
  undefined,  // year
  undefined,  // title
  10
);
```
<｜tool▁calls▁begin｜><｜tool▁call▁begin｜>
read_file

#### Complete Example with TMDB Integration

```typescript
const API_BASE_URL = 'https://tmdb-semantic-recommender.onrender.com';
const TMDB_API_KEY = 'your-tmdb-api-key';
const TMDB_BASE_URL = 'https://api.themoviedb.org/3';

async function getRecommendedMoviesWithDetails(
  synopsis: string,
  genre?: string,
  year?: number,
  title?: string,
  topK: number = 10
) {
  try {
    // 1. Get recommendations from our API (with context metadata)
    const recommendationResponse = await fetch(
      `${API_BASE_URL}/api/v1/recommend`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          synopsis, 
          genre,
          year,
          title,
          top_k: topK 
        }),
      }
    );

    if (!recommendationResponse.ok) {
      throw new Error('Failed to get recommendations');
    }

    const { recommendations } = await recommendationResponse.json();

    // 2. Fetch full movie details from TMDB
    const moviesWithDetails = await Promise.all(
      recommendations.map(async (rec: MovieRecommendation) => {
        const tmdbResponse = await fetch(
          `${TMDB_BASE_URL}/movie/${rec.movie_id}?api_key=${TMDB_API_KEY}`
        );
        
        if (!tmdbResponse.ok) {
          return {
            ...rec,
            tmdb_data: null,
          };
        }

        const tmdbData = await tmdbResponse.json();
        return {
          ...rec,
          tmdb_data: {
            poster_path: tmdbData.poster_path,
            backdrop_path: tmdbData.backdrop_path,
            release_date: tmdbData.release_date,
            genres: tmdbData.genres,
            vote_average: tmdbData.vote_average,
            runtime: tmdbData.runtime,
          },
        };
      })
    );

    return moviesWithDetails;
  } catch (error) {
    console.error('Error:', error);
    throw error;
  }
}

// Usage in React component (with metadata from TMDB)
function MovieRecommendations({ 
  synopsis, 
  genre, 
  year, 
  title 
}: { 
  synopsis: string;
  genre?: string;
  year?: number;
  title?: string;
}) {
  const [movies, setMovies] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchRecommendations() {
      setLoading(true);
      setError(null);
      try {
        const results = await getRecommendedMoviesWithDetails(
          synopsis,
          genre,  // optional but recommended
          year,   // optional but recommended
          title,  // optional but recommended
          10
        );
        setMovies(results);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    }

    if (synopsis && synopsis.length >= 10) {
      fetchRecommendations();
    }
  }, [synopsis, genre, year, title]);

  if (loading) return <div>Loading recommendations...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      {movies.map((movie) => (
        <div key={movie.movie_id}>
          <h3>{movie.tmdb_data?.title || movie.title}</h3>
          <p>Similarity: {(movie.similarity_score * 100).toFixed(1)}%</p>
          {movie.tmdb_data?.poster_path && (
            <img
              src={`https://image.tmdb.org/t/p/w200${movie.tmdb_data.poster_path}`}
              alt={movie.title || 'Movie poster'}
            />
          )}
        </div>
      ))}
    </div>
  );
}
```

### React Hook Example

```typescript
import { useState, useCallback } from 'react';

const API_BASE_URL = 'https://tmdb-semantic-recommender.onrender.com';

export function useRecommendations() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<RecommendationResponse | null>(null);

  const getRecommendations = useCallback(async (
    synopsis: string,
    genre?: string,
    year?: number,
    title?: string,
    topK: number = 10
  ) => {
    if (synopsis.length < 10) {
      setError('Synopsis must be at least 10 characters');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/recommend`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ synopsis, genre, year, title, top_k: topK }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to get recommendations');
      }

      const result = await response.json();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      setData(null);
    } finally {
      setLoading(false);
    }
  }, []);

  return { getRecommendations, loading, error, data };
}
```

### Axios Example

```typescript
import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'https://tmdb-semantic-recommender.onrender.com',
  headers: {
    'Content-Type': 'application/json',
  },
});

export async function getRecommendations(
  synopsis: string,
  genre?: string,
  year?: number,
  title?: string,
  topK: number = 10
) {
  try {
    const response = await apiClient.post<RecommendationResponse>(
      '/api/v1/recommend',
      { synopsis, genre, year, title, top_k: topK }
    );
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(error.response?.data?.detail || error.message);
    }
    throw error;
  }
}
```

---

## ⚠️ Error Handling

### Common Error Scenarios

| Status Code | Error | Solution |
|------------|-------|----------|
| `400` | Synopsis too short | Ensure synopsis is at least 10 characters |
| `400` | Synopsis too long | Limit synopsis to 5000 characters |
| `400` | Invalid top_k | Use top_k between 1 and 50 |
| `500` | Server error | Retry request or check service status |
| `503` | Model not loaded | Check `/health` endpoint, wait and retry |

### Error Handling Example

```typescript
async function getRecommendationsSafe(
  synopsis: string,
  genre?: string,
  year?: number,
  title?: string,
  topK: number = 10
) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/recommend`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ synopsis, genre, year, title, top_k: topK }),
    });

    const data = await response.json();

    if (!response.ok) {
      // Handle specific error cases
      switch (response.status) {
        case 400:
          throw new Error(`Validation error: ${data.detail}`);
        case 503:
          throw new Error('Service temporarily unavailable. Please try again later.');
        case 500:
          throw new Error('Server error. Please try again.');
        default:
          throw new Error(data.detail || 'Unknown error');
      }
    }

    return data;
  } catch (error) {
    if (error instanceof TypeError) {
      // Network error
      throw new Error('Network error. Please check your connection.');
    }
    throw error;
  }
}
```

---

## 🎯 Best Practices

### 1. Always Check Health Before Requests

```typescript
async function isServiceReady(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    if (response.ok) {
      const data = await response.json();
      return data.model_loaded === true;
    }
    return false;
  } catch {
    return false;
  }
}

// Before making recommendations
if (await isServiceReady()) {
  const recommendations = await getRecommendations(
    synopsis,
    genre,   // optional but recommended
    year,    // optional but recommended
    title    // optional but recommended
  );
}
```

### 2. Validate Input Before Sending

```typescript
function validateSynopsis(synopsis: string): { valid: boolean; error?: string } {
  if (synopsis.length < 10) {
    return { valid: false, error: 'Synopsis must be at least 10 characters' };
  }
  if (synopsis.length > 5000) {
    return { valid: false, error: 'Synopsis must be less than 5000 characters' };
  }
  return { valid: true };
}
```

### 3. Implement Retry Logic

```typescript
async function getRecommendationsWithRetry(
  synopsis: string,
  genre?: string,
  year?: number,
  title?: string,
  topK: number = 10,
  maxRetries: number = 3
): Promise<RecommendationResponse> {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await getRecommendations(synopsis, genre, year, title, topK);
    } catch (error) {
      if (attempt === maxRetries) throw error;
      // Wait before retrying (exponential backoff)
      await new Promise(resolve => setTimeout(resolve, attempt * 1000));
    }
  }
  throw new Error('Max retries exceeded');
}
```

### 4. Handle Loading States

```typescript
const [state, setState] = useState<{
  loading: boolean;
  error: string | null;
  data: RecommendationResponse | null;
}>({
  loading: false,
  error: null,
  data: null,
});

const fetchRecommendations = async (
  synopsis: string,
  genre?: string,
  year?: number,
  title?: string
) => {
  setState({ loading: true, error: null, data: null });
  try {
    const data = await getRecommendations(synopsis, genre, year, title);
    setState({ loading: false, error: null, data });
  } catch (error) {
    setState({
      loading: false,
      error: error instanceof Error ? error.message : 'Unknown error',
      data: null,
    });
  }
};
```

---

## 📊 Response Data Usage

### Understanding the Recommendations

**How the model works:**
- The API receives a synopsis (overview) and optionally genre, year, and title from your frontend
- Internally, it builds a **context-enriched query** in the format:
  ```
  "Genre: {genres}. Year: {year}. Title: {title}. Overview: {overview}"
  ```
- This enriched query is then encoded into embeddings using **context-aware processing**
- The model searches across **30,000 pre-processed movies** with enriched metadata
- Results are ranked by semantic similarity (0.0 to 1.0)

**Why recommendations are better now:**
- **Context-aware embeddings** prevent genre confusion (e.g., Horror won't mix with Romance)
- **Metadata enrichment** creates semantic anchors that dramatically improve accuracy
- **Larger library** (30k vs 10k) means better coverage and more accurate matches
- **When you provide genre/year/title**, the API uses the same format as the training data, resulting in much better matches

**Best Practice**: Always provide genre, year, and title when available for optimal results!

### Using `movie_id` with TMDB API

The `movie_id` returned in recommendations corresponds to TMDB movie IDs. Use it to fetch full movie details:

```typescript
// Get full movie details from TMDB
const tmdbResponse = await fetch(
  `https://api.themoviedb.org/3/movie/${movie_id}?api_key=${TMDB_API_KEY}`
);
const movieDetails = await tmdbResponse.json();

// Available fields:
// - poster_path, backdrop_path
// - title, overview, release_date
// - genres, runtime, vote_average
// - etc.
```

### Using `similarity_score`

The similarity score ranges from 0.0 to 1.0 (cosine similarity):
- `0.9-1.0` = Excellent match (highly recommended)
- `0.75-0.89` = Very similar (strong recommendation)
- `0.6-0.74` = Similar (good match)
- `< 0.6` = Less similar (lower confidence)

**Note**: With the new context-aware model, scores may appear slightly lower than before (0.65-0.75 is common for good matches), but the **quality and relevance** of recommendations is significantly improved. The model is now more discerning and won't recommend movies just because they share common words—they need to share thematic context.

Display format:
```typescript
const percentage = (movie.similarity_score * 100).toFixed(1); // "75.2%"
const stars = Math.round(movie.similarity_score * 5); // 1-5 stars rating
```

---

## 🔄 Rate Limiting

Currently, **no rate limiting is implemented**. However, consider implementing client-side throttling for better UX:

```typescript
let lastRequestTime = 0;
const MIN_REQUEST_INTERVAL = 500; // 500ms between requests

function throttledGetRecommendations(
  synopsis: string,
  genre?: string,
  year?: number,
  title?: string,
  topK: number = 10
) {
  const now = Date.now();
  if (now - lastRequestTime < MIN_REQUEST_INTERVAL) {
    return Promise.reject(new Error('Please wait before making another request'));
  }
  lastRequestTime = now;
  return getRecommendations(synopsis, genre, year, title, topK);
}
```

---

## 📝 TypeScript Definitions

Complete TypeScript definitions for your project:

```typescript
// types/api.ts

export interface RecommendationRequest {
  synopsis: string;      // Required
  genre?: string;        // Optional (recommended for better accuracy)
  year?: number;         // Optional (recommended for better accuracy)
  title?: string;        // Optional (recommended for better accuracy)
  top_k?: number;        // Optional, default: 10
}

export interface MovieRecommendation {
  movie_id: number;
  similarity_score: number;
  title: string | null;
  overview: string | null;
}

export interface RecommendationResponse {
  query: string;
  recommendations: MovieRecommendation[];
  count: number;
}

export interface HealthResponse {
  status: 'healthy' | 'unhealthy';
  model_loaded: boolean;
}

export interface APIInfoResponse {
  message: string;
  version: string;
  status: string;
  docs: string;
}
```

---

## 🧪 Testing Endpoints

### Using cURL

```bash
# Health check
curl https://tmdb-semantic-recommender.onrender.com/health

# Get recommendations with metadata (recommended)
curl -X POST https://tmdb-semantic-recommender.onrender.com/api/v1/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "synopsis": "When Ellen, the matriarch of the Graham family, passes away, her daughters family begins to unravel cryptic and increasingly terrifying secrets about their ancestry.",
    "genre": "Horror, Mystery, Thriller",
    "year": 2018,
    "title": "Hereditary",
    "top_k": 5
  }'

# Without metadata (works, but less accurate)
curl -X POST https://tmdb-semantic-recommender.onrender.com/api/v1/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "synopsis": "A space opera about rebels fighting an empire",
    "top_k": 5
  }'
```

### Using Postman / Insomnia

1. Import the collection
2. Set base URL: `https://tmdb-semantic-recommender.onrender.com`
3. Test endpoints

---

## 📞 Support

For issues or questions:
- Check interactive docs: `https://tmdb-semantic-recommender.onrender.com/docs`
- Open an issue on GitHub
- Contact the backend team

---

**Last Updated:** 2024  
**API Version:** 1.0.0

