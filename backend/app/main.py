"""
CareerCrew Backend Main Application.
Privacy-First Local Multi-Agent Job Application Optimizer.
Zero external paid cloud or LLM API dependencies.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.logging import logger, setup_logging
from app.db.init_db import init_db
from app.services.vector_store import vector_store
from app.api.v1.api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifecycle management.
    Performs local database table migrations and vector store persistence initialization.
    """
    setup_logging(settings.LOG_LEVEL)
    logger.info("=" * 60)
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Local LLM Provider: {settings.LLM_PROVIDER} ({settings.OLLAMA_MODEL})")
    logger.info(f"Local Embeddings: {settings.OLLAMA_EMBED_MODEL}")
    logger.info(f"Local Database: {settings.DATABASE_URL}")
    logger.info(f"Local Vector Store: {settings.VECTOR_STORE_DIR}")
    logger.info("ZERO external cloud APIs permitted or configured.")
    logger.info("=" * 60)

    # 1. Initialize SQLite database tables
    try:
        init_db()
    except Exception as exc:
        logger.error(f"Failed to initialize database during startup: {exc}")

    # 2. Initialize local vector store
    try:
        vector_store.initialize()
    except Exception as exc:
        logger.warning(f"Vector store lazy initialization warning: {exc}")

    yield

    logger.info(f"Shutting down {settings.APP_NAME} cleanly...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Privacy-First Local Multi-Agent Job Application Optimizer. "
        "Runs entirely on local hardware with Ollama, CrewAI, SQLite, and ChromaDB."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS configuration for local Next.js frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Safely log and return exceptions without exposing stack traces or sensitive data."""
    logger.error(f"Unhandled server error on {request.method} {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Application data remains safely local."},
    )


# Mount API routes under /api
app.include_router(api_router, prefix="/api")


# Root landing endpoint for sanity check
@app.get("/", tags=["Root"])
async def root():
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "mode": "privacy-first-local",
        "documentation": "/docs",
        "health": "/api/health",
        "system_status": "/api/system/status",
    }
