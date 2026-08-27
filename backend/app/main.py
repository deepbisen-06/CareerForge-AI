from fastapi import FastAPI, Request, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import time

from app.core.config import settings
from app.core.logging_config import setup_logging
from app.database.session import engine, Base, SessionLocal
from app.models.entities import Internship
from app.rag.vector_store import rag_store

from app.api.auth import router as auth_router
from app.api.profile import router as profile_router
from app.api.resume import router as resume_router
from app.api.internships import router as internships_router
from app.api.matching import router as matching_router
from app.api.skill_gaps import router as skill_gaps_router
from app.api.documents import router as documents_router
from app.api.interview import router as interview_router
from app.api.applications import router as applications_router
from app.api.chat import router as chat_router
from app.api.notifications import router as notifications_router
from app.api.dashboard import router as dashboard_router
from app.api.admin import router as admin_router
from app.api.agent import router as agent_router

setup_logging()
logger = logging.getLogger("careerbridge.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure tables exist & index internships in Hybrid RAG Vector Store
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        active_internships = db.query(Internship).filter(Internship.is_active == True).all()
        if active_internships:
            records = [{
                "id": item.id,
                "company": item.company,
                "title": item.title,
                "domain": item.domain,
                "description": item.description,
                "requirements": item.requirements or [],
                "preferred_skills": item.preferred_skills or [],
                "location": item.location,
                "work_mode": item.work_mode,
                "stipend": item.stipend,
                "duration": item.duration,
                "eligibility": item.eligibility,
                "deadline": item.deadline,
                "application_url": item.application_url,
                "source": item.source,
                "source_type": getattr(item, "source_type", "CURATED"),
                "company_logo_url": getattr(item, "company_logo_url", None),
                "is_active": item.is_active,
                "is_demo": item.is_demo
            } for item in active_internships]
            rag_store.index_internships(records)
            logger.info(f"Loaded and indexed {len(records)} active internships into Hybrid RAG engine.")
    finally:
        db.close()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="CareerBridge AI — AI-powered career guidance, matching and application platform.",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Structured Request Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration_ms = round((time.time() - start_time) * 1000, 2)
    logger.info(
        f"{request.method} {request.url.path} -> {response.status_code} ({duration_ms}ms)",
        extra={"duration_ms": duration_ms, "status": response.status_code}
    )
    return response

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled server exception on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred. Please try again or contact support."
            }
        }
    )

# Mount API Routers under /api/v1
api_prefix = settings.API_V1_STR
app.include_router(auth_router, prefix=api_prefix)
app.include_router(profile_router, prefix=api_prefix)
app.include_router(resume_router, prefix=api_prefix)
app.include_router(internships_router, prefix=api_prefix)
app.include_router(matching_router, prefix=api_prefix)
app.include_router(skill_gaps_router, prefix=api_prefix)
app.include_router(documents_router, prefix=api_prefix)
app.include_router(interview_router, prefix=api_prefix)
app.include_router(applications_router, prefix=api_prefix)
app.include_router(chat_router, prefix=api_prefix)
app.include_router(notifications_router, prefix=api_prefix)
app.include_router(dashboard_router, prefix=api_prefix)
app.include_router(admin_router, prefix=api_prefix)
app.include_router(agent_router, prefix=api_prefix)

# Health & Status Endpoints
@app.get("/health")
@app.get(f"{api_prefix}/health")
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "rag_indexed_documents": len(rag_store.documents)
    }

@app.get(f"{api_prefix}/health/db")
def health_db():
    db = SessionLocal()
    try:
        count = db.query(Internship).count()
        return {"status": "connected", "total_internships": count}
    finally:
        db.close()

@app.get(f"{api_prefix}/health/rag")
def health_rag():
    return {
        "status": "indexed" if rag_store.is_indexed else "unindexed",
        "documents_count": len(rag_store.documents)
    }

@app.get("/")
def root():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "docs": "/docs"
    }
