from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn
import logging
from prometheus_client import make_asgi_app

from api import chat, analytics, feedback, knowledge, profile

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up application...")
    # TODO: Initialize database connections, load models, etc.
    yield
    # Shutdown
    logger.info("Shutting down application...")
    # TODO: Close database connections, cleanup resources, etc.

app = FastAPI(
    title="Customer Support Agent Demo API",
    description="API for the autonomous customer support agent system",
    version="1.0.0",
    lifespan=lifespan
)

# Prometheus metrics endpoint
app.mount("/metrics", make_asgi_app())

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])
app.include_router(feedback.router, prefix="/api/v1/feedback", tags=["feedback"])
app.include_router(knowledge.router, prefix="/api/v1/knowledge", tags=["knowledge"])
app.include_router(profile.router, prefix="/api/v1/user", tags=["user"])

# Optionally serve static files (for docs or demo)
# app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return {"message": "Welcome to the Customer Support Agent API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/v1/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 