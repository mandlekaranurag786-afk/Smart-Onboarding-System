"""
FastAPI application for OnboardIQ
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="OnboardIQ API",
    description="Multi-Agent Onboarding System",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Next.js frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialized")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "OnboardIQ API",
        "version": "1.0.0"
    }

@app.get("/health")
async def health():
    """Health check"""
    return {"status": "healthy"}

# Import routers
from app.api import candidates, tasks, stakeholders, reasoning

# Register routers
app.include_router(candidates.router, prefix="/api/candidates", tags=["Candidates"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])
app.include_router(stakeholders.router, prefix="/api/stakeholders", tags=["Stakeholders"])
app.include_router(reasoning.router, prefix="/api/reasoning", tags=["Reasoning"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
