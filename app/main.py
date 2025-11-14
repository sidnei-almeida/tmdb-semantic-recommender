"""
FastAPI application for movie recommendation based on synopsis similarity.
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from app.api.routes import router
from app.core.config import settings
from app.services.model_service import ModelService, set_model_service

# Global model service instance
model_service: ModelService | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    Loads the model on startup and cleans up on shutdown.
    """
    global model_service
    
    # Startup: Load model
    try:
        print("Loading model and index...")
        model_service = ModelService(
            model_path=settings.MODEL_PATH,
            index_path=settings.INDEX_PATH,
            movies_map_path=settings.MOVIES_MAP_PATH,
        )
        model_service.load()
        set_model_service(model_service)
        print("Model and index loaded successfully!")
    except Exception as e:
        print(f"Error loading model: {e}")
        raise
    
    yield
    
    # Shutdown: Cleanup (if needed)
    model_service = None
    set_model_service(None)


app = FastAPI(
    title="TMDB Semantic Recommender API",
    description="High-Performance Movie Recommendation API based on Content Similarity using Deep Learning (BERT/ONNX) and Vector Search",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "TMDB Semantic Recommender API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    from app.services.model_service import get_model_service_instance
    
    model_service_instance = get_model_service_instance()
    
    if model_service_instance is None or not model_service_instance.is_loaded:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    return {
        "status": "healthy",
        "model_loaded": model_service_instance.is_loaded,
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "An error occurred",
        },
    )


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=settings.DEBUG,
    )

