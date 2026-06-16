import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import system_logger
from app.db.session import create_db_and_tables, SessionLocal
from app.models.rag import KnowledgeBase
from app.rag.ingestion import IngestionManager
from app.api.router import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    system_logger.info("Starting up BuildWise AI FastAPI Server...")
    try:
        # Create tables and seed roles
        create_db_and_tables()
        system_logger.info("Database schemas and seeding verified successfully.")
        
        # Database schemas and roles are seeded
        pass
            
    except Exception as e:
        system_logger.error(f"Error during application startup initialization: {str(e)}", exc_info=True)
    
    yield
    # Shutdown actions
    system_logger.info("Shutting down BuildWise AI FastAPI Server...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Set CORS middleware
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin).strip("/") for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Register central router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Global health check route
@app.get("/health", status_code=status.HTTP_200_OK, tags=["Health"])
def health_check():
    return {"status": "healthy", "service": settings.PROJECT_NAME}

# Standardized Error Handlers
@app.exception_handler(Exception)
def global_exception_handler(request: Request, exc: Exception):
    system_logger.error(f"Unhandled system error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected server error occurred. Please try again later."}
    )
