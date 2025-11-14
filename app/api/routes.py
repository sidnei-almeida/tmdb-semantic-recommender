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
        description="Movie synopsis to find similar movies",
        example="A young wizard discovers his magical heritage and must face the dark lord who killed his parents.",
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
    description="Given a movie synopsis, returns similar movies based on semantic similarity using BERT embeddings.",
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
        # Get recommendations
        recommendations = model_service.recommend(
            synopsis=request.synopsis,
            top_k=request.top_k,
        )
        
        return RecommendationResponse(
            query=request.synopsis,
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

