"""
Main FastAPI Application
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .core.config import get_settings
from .core.logging import logger
from .db import init_db
from .api import health_checks, capabilities
from app.api import health
from app.api import overview
from datetime import datetime, timezone
from fastapi.middleware.cors import CORSMiddleware




settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown"""
    # Startup
    logger.info("Starting Infrastructure Analyzer Dashboard")
    # init_db()   # ⛔ disabled for local run (no postgres)
    logger.info("Database init skipped (local)")
    
    yield

    
    # Shutdown
    logger.info("Shutting down Infrastructure Analyzer Dashboard")


# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION,
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(health_checks.router)
app.include_router(capabilities.router)
app.include_router(health.router, prefix="/api")
app.include_router(overview.router)




@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Infrastructure Analyzer Dashboard API",
        "version": settings.VERSION,
        "docs_url": "/docs",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "up",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    from datetime import datetime
    
    uvicorn.run(
        app,
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD,
        log_level=settings.API_LOG_LEVEL,
    )
