"""
FastAPI Application Entry Point for Customer Support Agent Demo API

This module sets up the main FastAPI application with all necessary middleware,
routing, monitoring capabilities, and lifecycle management for a production-ready
customer support AI system.

Key Features:
- Multi-agent AI routing for different support categories
- Real-time WebSocket communication for chat interface
- Prometheus metrics collection for monitoring
- CORS middleware for cross-origin requests
- Structured logging configuration
- Health check endpoints for deployment monitoring

The application follows a microservice architecture pattern with separate
routers for different functional areas (chat, analytics, feedback, etc.)
"""

from dotenv import load_dotenv
# Load environment variables first to ensure all configuration is available
# before importing other modules that may depend on environment settings
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn
import logging
from prometheus_client import make_asgi_app

# Import all API routers for different functional areas
from src.api import chat, analytics, feedback, knowledge, profile

# Configure structured logging for production monitoring
# This setup ensures consistent log formatting across the application
# with timestamps, log levels, and module names for better debugging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown events.
    
    This context manager handles the initialization and cleanup of resources
    that need to persist throughout the application lifecycle, such as:
    - Database connection pools
    - ML model loading
    - Cache initialization
    - Background task setup
    
    The startup phase occurs before the application begins serving requests,
    while shutdown ensures graceful cleanup when the application terminates.
    """
    # Startup phase - initialize resources
    logger.info("Starting up application...")
    # TODO: Initialize database connections, load models, etc.
    # Example startup tasks:
    # - Initialize database connection pool
    # - Load pre-trained ML models into memory
    # - Set up Redis connections for caching
    # - Initialize background task queues
    
    yield  # Application runs here
    
    # Shutdown phase - cleanup resources
    logger.info("Shutting down application...")
    # TODO: Close database connections, cleanup resources, etc.
    # Example shutdown tasks:
    # - Close database connection pools
    # - Save model states or cache data
    # - Cancel background tasks
    # - Release file handles and network connections

# Initialize FastAPI application with comprehensive metadata
# The lifespan parameter ensures proper resource management
app = FastAPI(
    title="Customer Support Agent Demo API",
    description="API for the autonomous customer support agent system",
    version="1.0.0",
    lifespan=lifespan
)

# Mount Prometheus metrics endpoint for monitoring
# This provides real-time metrics that can be scraped by monitoring systems
# to track API performance, request volumes, error rates, etc.
app.mount("/metrics", make_asgi_app())

# Configure CORS (Cross-Origin Resource Sharing) middleware
# This is essential for web applications where the frontend and backend
# are served from different domains or ports during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Configure this properly for production
    # Production security note: Replace ["*"] with specific allowed origins
    # Example: ["https://yourdomain.com", "https://app.yourdomain.com"]
    allow_credentials=True,  # Allow cookies and authentication headers
    allow_methods=["*"],     # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],     # Allow all headers including custom ones
)

# Register API routers with versioned prefixes and tags
# This modular approach allows for easy API versioning and organization
# Each router handles a specific domain of functionality
app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])
app.include_router(feedback.router, prefix="/api/v1/feedback", tags=["feedback"])
app.include_router(knowledge.router, prefix="/api/v1/knowledge", tags=["knowledge"])
app.include_router(profile.router, prefix="/api/v1/user", tags=["user"])

# Optional static file serving for documentation or demo content
# Uncomment when static assets are needed (images, docs, etc.)
# app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    """
    Root endpoint providing basic API information.
    
    Returns a welcome message that can be used to verify the API is running.
    This is often the first endpoint hit by monitoring systems or developers
    testing the API connectivity.
    """
    return {"message": "Welcome to the Customer Support Agent API"}

@app.get("/health")
async def health_check():
    """
    Health check endpoint for deployment and monitoring systems.
    
    This endpoint should be lightweight and return quickly to indicate
    that the application is running and responsive. Load balancers and
    container orchestration systems typically use this for health checks.
    
    In production, this could be enhanced to check:
    - Database connectivity
    - External service availability
    - Memory/CPU usage thresholds
    - Cache system status
    """
    return {"status": "healthy"}

@app.get("/api/v1/health")
def health():
    """
    Versioned health check endpoint for API-specific monitoring.
    
    This duplicates the functionality of /health but under the API version
    namespace, allowing for API-specific health monitoring that's separate
    from general application health checks.
    """
    return {"status": "ok"}

# Application entry point for direct execution
# This allows the application to be run directly with `python main.py`
# while also supporting deployment via WSGI/ASGI servers
if __name__ == "__main__":
    # Development server configuration
    # In production, this would typically be replaced with a production
    # WSGI server like Gunicorn or Uvicorn in a container/deployment setup
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 