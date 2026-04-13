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
from app.api import (
    candidates, tasks, stakeholders, reasoning, emails,
    auth, meetings, chat, analytics, notifications, settings, employees,
    scheduling,
    activities,
    it_tasks,
    email_webhook
)
from routes.analytics import router as analytics_router

try:
    from app.api import rag
    RAG_ROUTER_AVAILABLE = True
except Exception as exc:
    logger.warning(f"RAG router disabled during startup: {exc}")
    RAG_ROUTER_AVAILABLE = False

# Register routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(candidates.router, prefix="/api/candidates", tags=["Candidates"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])
app.include_router(it_tasks.router, prefix="/api/it-tasks", tags=["IT Tasks"])
app.include_router(email_webhook.router, prefix="/api", tags=["Email Webhook"])
app.include_router(stakeholders.router, prefix="/api/stakeholders", tags=["Stakeholders"])
app.include_router(meetings.router, prefix="/api/meetings", tags=["Meetings"])
app.include_router(scheduling.router, prefix="/api/schedule", tags=["Scheduling"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(analytics_router, prefix="/api")
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["Notifications"])
app.include_router(settings.router, prefix="/api/settings", tags=["Settings"])
app.include_router(employees.router, prefix="/api/employees", tags=["Employees"])
app.include_router(reasoning.router, prefix="/api/reasoning", tags=["Reasoning"])
app.include_router(emails.router, prefix="/api/emails", tags=["Emails"])
app.include_router(activities.router, prefix="/api/activities", tags=["Activities"])

if RAG_ROUTER_AVAILABLE:
    app.include_router(rag.router, tags=["RAG"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
