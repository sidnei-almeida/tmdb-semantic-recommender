"""
API routes for movie recommendations.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional

from app.services.model_service import ModelService, get_model_service

router = APIRouter(tags=["recommendations"])


class RecommendationRequest(BaseModel):
    """
    Request model for movie recommendations.
    Supports both Warm Start (tmdb_id only) and Cold Start (full payload).
    """
    
    tmdb_id: int = Field(..., description="TMDB movie ID")
    top_k: int = Field(
        default=50,
        ge=1,
        le=100,
        description="Number of similar movies to return (default: 50)",
    )
    
    # Cold Start fields (optional - required only if tmdb_id not in movies_map)
    title: Optional[str] = Field(
        None,
        max_length=200,
        description="Movie title (required for Cold Start)",
    )
    overview: Optional[str] = Field(
        None,
        max_length=5000,
        description="Movie overview/synopsis (required for Cold Start)",
    )
    genres: Optional[List[str]] = Field(
        None,
        description="List of genres (required for Cold Start)",
        example=["Science Fiction", "Horror"],
    )
    directors: Optional[List[str]] = Field(
        None,
        description="List of directors (optional for Cold Start)",
        example=["Some Director"],
    )
    studios: Optional[List[str]] = Field(
        None,
        description="List of studios (optional for Cold Start)",
        example=["Some Studio"],
    )
    countries: Optional[List[str]] = Field(
        None,
        description="List of countries (optional for Cold Start)",
        example=["USA"],
    )
    year: Optional[int] = Field(
        None,
        ge=1888,
        le=2100,
        description="Release year (optional for Cold Start)",
    )
    keywords: Optional[List[str]] = Field(
        None,
        description="List of keywords (optional for Cold Start)",
        example=["monster", "future"],
    )


class MovieRecommendation(BaseModel):
    """Movie recommendation response model."""
    
    tmdb_id: int = Field(..., description="TMDB movie ID")
    title: str = Field(..., description="Movie title")
    year: str = Field(..., description="Release year")
    poster_path: Optional[str] = Field(None, description="Poster path")
    genres_list: List[str] = Field(..., description="List of genres")


@router.post(
    "/recommend",
    response_model=List[MovieRecommendation],
    summary="Get movie recommendations (Warm/Cold Start)",
    description="Retrieval engine that returns Top 50 similar movies. Supports Warm Start (tmdb_id only) and Cold Start (full payload for new movies). Returns a list of movies for front-end re-ranking.",
)
async def get_recommendations(
    request: RecommendationRequest,
    model_service: ModelService = Depends(get_model_service),
) -> List[MovieRecommendation]:
    """
    Get movie recommendations using Warm Start or Cold Start.
    
    Warm Start: If tmdb_id exists in movies_map, uses pre-computed embedding.
    Cold Start: If tmdb_id not found, builds metadata soup from payload and generates embedding on-the-fly.
    
    Args:
        request: Recommendation request (Warm or Cold Start)
        model_service: Injected model service dependency
        
    Returns:
        List of MovieRecommendation objects (Top 50 by default)
        
    Raises:
        HTTPException: If model is not loaded or processing fails
    """
    if not model_service.is_loaded:
        raise HTTPException(
            status_code=503,
            detail="Model service is not loaded. Please try again later.",
        )
    
    try:
        # Get recommendations using Warm/Cold Start logic
        recommendations = model_service.recommend(
            tmdb_id=request.tmdb_id,
            top_k=request.top_k,
            # Cold Start fields
            title=request.title,
            overview=request.overview,
            genres=request.genres,
            directors=request.directors,
            studios=request.studios,
            countries=request.countries,
            year=request.year,
            keywords=request.keywords,
        )
        
        return recommendations
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}",
        )

