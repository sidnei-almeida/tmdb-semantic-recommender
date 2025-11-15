"""
API routes for movie recommendations.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from app.services.model_service import ModelService, get_model_service

router = APIRouter(tags=["recommendations"])


class RecommendationRequest(BaseModel):
    """Request model for movie recommendations."""
    
    synopsis: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="Movie synopsis/overview to find similar movies",
        example="When Ellen, the matriarch of the Graham family, passes away, her daughter's family begins to unravel cryptic and increasingly terrifying secrets about their ancestry.",
    )
    genre: str | None = Field(
        None,
        description="Movie genre(s) for context-aware recommendations (e.g., 'Horror, Mystery, Thriller')",
        example="Horror, Mystery, Thriller",
    )
    year: int | None = Field(
        None,
        ge=1888,
        le=2100,
        description="Release year of the movie for context-aware recommendations",
        example=2018,
    )
    title: str | None = Field(
        None,
        max_length=200,
        description="Movie title for context-aware recommendations",
        example="Hereditary",
    )
    top_k: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Number of similar movies to return",
    )


class MovieRecommendation(BaseModel):
    """Movie recommendation response model."""
    
    movie_id: int = Field(..., description="Movie ID (can be used with TMDB API)")
    similarity_score: float = Field(..., description="Similarity score (0-1)")
    title: str | None = Field(None, description="Movie title if available in mapping")
    overview: str | None = Field(None, description="Movie overview if available in mapping")


class RecommendationResponse(BaseModel):
    """Response model for movie recommendations."""
    
    query: str = Field(..., description="Original synopsis query")
    recommendations: list[MovieRecommendation] = Field(..., description="List of recommended movies")
    count: int = Field(..., description="Number of recommendations returned")


@router.post(
    "/recommend",
    response_model=RecommendationResponse,
    summary="Get movie recommendations based on synopsis",
    description="Given a movie synopsis (and optionally genre, year, title), returns Top 30 similar movies based on context-aware semantic similarity. The API always returns 30 results for the front-end to perform hybrid re-ranking. The API will enrich the query with metadata if provided for better accuracy.",
)
async def get_recommendations(
    request: RecommendationRequest,
    model_service: ModelService = Depends(get_model_service),
) -> RecommendationResponse:
    """
    Get movie recommendations based on synopsis similarity.
    
    Args:
        request: Recommendation request with synopsis and optional top_k
        model_service: Injected model service dependency
        
    Returns:
        RecommendationResponse with similar movies
        
    Raises:
        HTTPException: If model is not loaded or processing fails
    """
    if not model_service.is_loaded:
        raise HTTPException(
            status_code=503,
            detail="Model service is not loaded. Please try again later.",
        )
    
    try:
        # Get recommendations (with context-aware metadata if provided)
        recommendations = model_service.recommend(
            synopsis=request.synopsis,
            genre=request.genre,
            year=request.year,
            title=request.title,
            top_k=request.top_k,
        )
        
        # Build query string for response (showing enriched query if metadata provided)
        query_display = request.synopsis
        if request.genre or request.year or request.title:
            parts = []
            if request.genre:
                parts.append(f"Genre: {request.genre}")
            if request.year:
                parts.append(f"Year: {request.year}")
            if request.title:
                parts.append(f"Title: {request.title}")
            query_display = ". ".join(parts) + f". Overview: {request.synopsis}"
        
        return RecommendationResponse(
            query=query_display,
            recommendations=recommendations,
            count=len(recommendations),
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}",
        )

