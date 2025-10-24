"""
FastAPI application entry point.

Clean architecture with modular routing.
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import structlog

from src.core.config import get_settings
from src.core.exceptions import SmartSaludException
from src.database.connection import init_db, close_db, get_engine

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Startup:
    - Configure logging
    - Initialize database connection
    - Create tables (dev only)
    - Log application start

    Shutdown:
    - Close database connections
    - Log application shutdown
    """
    # Get settings
    settings = get_settings()

    # Configure structured logging
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.dev.ConsoleRenderer() if settings.app_env == "development"
            else structlog.processors.JSONRenderer()
        ],
        logger_factory=structlog.PrintLoggerFactory(),
    )

    # Startup
    logger.info(
        "application_starting",
        app_name=settings.app_name,
        environment=settings.app_env
    )

    # Initialize database
    engine = get_engine()
    logger.info("database_connection_initialized")

    # Create tables in development (production uses Alembic)
    if settings.app_env == "development":
        await init_db()
        logger.info("database_tables_created")

    yield

    # Shutdown
    logger.info("application_shutting_down")
    await close_db()
    logger.info("database_connections_closed")


# Create FastAPI app
app = FastAPI(
    title="smartSalud_V2",
    description="WhatsApp bot for medical appointment confirmations",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(SmartSaludException)
async def smartsalud_exception_handler(request: Request, exc: SmartSaludException):
    """Handle custom SmartSalud exceptions."""
    logger.error(
        "smartsalud_exception",
        error=exc.to_dict(),
        path=request.url.path
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": exc.message,
            "type": exc.__class__.__name__
        }
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint.

    Returns application status and configuration.
    Used by Railway and monitoring systems.
    """
    settings = get_settings()
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "environment": settings.app_env,
        "version": "2.0.0"
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with basic info."""
    settings = get_settings()
    return {
        "message": "smartSalud_V2 API",
        "version": "2.0.0",
        "docs": "/docs" if settings.app_env != "production" else "disabled",
        "health": "/health"
    }


# Router imports
from src.whatsapp.routes import router as whatsapp_router
from src.api.appointments import router as appointments_router
from src.api.doctors import router as doctors_router
from src.api.patients import router as patients_router
from src.api.stats import router as stats_router
from src.api.seed import router as seed_router
from src.elevenlabs.tools import router as elevenlabs_router

# Register routers
app.include_router(whatsapp_router)
app.include_router(appointments_router)
app.include_router(doctors_router)
app.include_router(patients_router)
app.include_router(stats_router, prefix="/api")
app.include_router(seed_router)  # Database seeding (temporary)
app.include_router(elevenlabs_router)  # ElevenLabs function calling


if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=(settings.app_env == "development")
    )
