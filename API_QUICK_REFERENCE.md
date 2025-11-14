# 🚀 API Quick Reference - Frontend Team

Quick reference guide for integrating with the TMDB Semantic Recommender API.

## 🆕 What's New

- **🧠 Context-Aware**: Model now uses genre/year/title context for better accuracy
- **📚 30k Movies**: Expanded from 10k to 30k films (300% more coverage)
- **⚡ Better Results**: Prevents semantic confusion (e.g., "family" in Horror ≠ Romance)

---

## Base URL

```
Production: https://tmdb-semantic-recommender.onrender.com
Local:      http://localhost:8000
```

---

## Main Endpoint

### Get Recommendations

```http
POST /api/v1/recommend
Content-Type: application/json

{
  "synopsis": "Movie synopsis/overview (10-5000 chars)",
  "genre": "Horror, Mystery, Thriller",  // Optional (recommended)
  "year": 2018,                            // Optional (recommended)
  "title": "Hereditary",                   // Optional (recommended)
  "top_k": 10                              // Optional, 1-50, default: 10
}
```

**Response (with metadata):**
```json
{
  "query": "Genre: Horror, Mystery, Thriller. Year: 2018. Title: Hereditary. Overview: When Ellen, the matriarch...",
  "recommendations": [
    {
      "movie_id": 2964,
      "similarity_score": 0.75,
      "title": "Hereditary",
      "overview": null
    }
  ],
  "count": 10
}
```

**Response (without metadata - less accurate):**
```json
{
  "query": "When Ellen, the matriarch...",
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

---

## JavaScript/TypeScript Quick Example

```typescript
// With metadata (recommended for better accuracy)
const response = await fetch('https://tmdb-semantic-recommender.onrender.com/api/v1/recommend', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    synopsis: "When Ellen, the matriarch of the Graham family, passes away, her daughter's family begins to unravel cryptic and increasingly terrifying secrets about their ancestry.",
    genre: "Horror, Mystery, Thriller",
    year: 2018,
    title: "Hereditary",
    top_k: 10
  })
});

const data = await response.json();

// Use movie_id with TMDB API
data.recommendations.forEach(movie => {
  // Fetch details from TMDB using movie.movie_id
  console.log(`${movie.movie_id}: ${movie.similarity_score.toFixed(2)} - ${movie.title}`);
});

// Without metadata (works, but less accurate)
const response2 = await fetch('https://tmdb-semantic-recommender.onrender.com/api/v1/recommend', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    synopsis: "A young wizard discovers his magical heritage",
    top_k: 10
  })
});
```

---

## Health Check

```typescript
const health = await fetch('https://tmdb-semantic-recommender.onrender.com/health');
const status = await health.json();
// { status: "healthy", model_loaded: true }
```

---

## TypeScript Types

```typescript
interface RecommendationRequest {
  synopsis: string;      // Required, 10-5000 chars
  genre?: string;        // Optional (recommended), e.g., "Horror, Mystery, Thriller"
  year?: number;         // Optional (recommended), 1888-2100
  title?: string;        // Optional (recommended), max 200 chars
  top_k?: number;        // Optional, 1-50, default: 10
}

interface MovieRecommendation {
  movie_id: number;           // Use with TMDB API
  similarity_score: number;   // 0.0 to 1.0 (cosine similarity)
  title: string | null;
  overview: string | null;
}

interface RecommendationResponse {
  query: string;                    // Shows enriched query if metadata provided
  recommendations: MovieRecommendation[];
  count: number;
}
```

## ⚠️ Important Notes

**Similarity Scores:**
- With the new context-aware model, scores may be slightly lower (0.65-0.75 is common for good matches)
- **Quality over quantity**: Lower scores but **better relevance** and **thematic consistency**
- The model is more discerning—it won't match movies just because they share words, they need shared context

**What Changed:**
- ✅ Better accuracy (context-aware embeddings)
- ✅ Larger library (30k vs 10k movies)
- ✅ Genre confusion prevention
- ⚠️ Scores may appear lower but quality is higher

## 📝 Important: New Request Format

The API now accepts **optional metadata fields** that dramatically improve accuracy:

- `genre`: Movie genre(s) separated by commas (e.g., "Horror, Mystery, Thriller")
- `year`: Release year (1888-2100)
- `title`: Movie title (max 200 chars)

**Why this matters:**
- When you provide genre/year/title, the API builds a context-enriched query:
  ```
  "Genre: {genres}. Year: {year}. Title: {title}. Overview: {overview}"
  ```
- This matches the format used during model training
- Results are **significantly more accurate** with metadata

**Example:**
```typescript
// Good (with metadata)
{ synopsis: "...", genre: "Horror", year: 2018, title: "Hereditary" }

// Works, but less accurate (without metadata)
{ synopsis: "..." }
```

---

## Error Handling

| Status | Meaning | Solution |
|--------|---------|----------|
| `400` | Invalid request | Check synopsis length (10-5000 chars) |
| `500` | Server error | Retry request |
| `503` | Service unavailable | Check `/health` endpoint |

---

## Validation Rules

- **synopsis**: Required, 10-5000 characters
- **genre**: Optional (recommended), string (e.g., "Horror, Mystery, Thriller")
- **year**: Optional (recommended), integer (1888-2100)
- **title**: Optional (recommended), string (max 200 characters)
- **top_k**: Optional, 1-50, default: 10

**Note**: While genre, year, and title are optional, providing them dramatically improves recommendation accuracy by enabling context-aware embeddings.

---

**Full Documentation:** See `API_DOCUMENTATION.md` for complete details.

