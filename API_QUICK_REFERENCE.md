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
  "synopsis": "Movie synopsis text (10-5000 chars)",
  "top_k": 10  // Optional, 1-50, default: 10
}
```

**Response:**
```json
{
  "query": "Original synopsis",
  "recommendations": [
    {
      "movie_id": 123,
      "similarity_score": 0.95,
      "title": "Movie Title",
      "overview": "Movie overview"
    }
  ],
  "count": 10
}
```

---

## JavaScript/TypeScript Quick Example

```typescript
const response = await fetch('https://tmdb-semantic-recommender.onrender.com/api/v1/recommend', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    synopsis: "A young wizard discovers his magical heritage",
    top_k: 10
  })
});

const data = await response.json();

// Use movie_id with TMDB API
data.recommendations.forEach(movie => {
  // Fetch details from TMDB using movie.movie_id
  console.log(`${movie.movie_id}: ${movie.similarity_score}`);
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
  synopsis: string;   // 10-5000 chars
  top_k?: number;     // 1-50, default: 10
}

interface MovieRecommendation {
  movie_id: number;           // Use with TMDB API
  similarity_score: number;   // 0.0 to 1.0 (cosine similarity)
  title: string | null;
  overview: string | null;
}

interface RecommendationResponse {
  query: string;
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
- **top_k**: Optional, 1-50, default: 10

---

**Full Documentation:** See `API_DOCUMENTATION.md` for complete details.

