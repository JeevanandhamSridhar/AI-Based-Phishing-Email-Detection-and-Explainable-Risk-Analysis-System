"""FastAPI Application Entrypoint

Configures middleware, CORS, lifespan startup/shutdown, error handlers, and routers.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import logger
from app.core.errors import register_error_handlers
from app.api.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan context manager for startup and shutdown events."""
    logger.info("Starting up %s (v%s)", settings.PROJECT_NAME, settings.VERSION)
    logger.info("Safety Invariant Check: OFFLINE_ONLY=%s, ALLOW_NETWORK_FETCH=%s", 
                settings.OFFLINE_ONLY, settings.ALLOW_NETWORK_FETCH)
    if not settings.validate_weights():
        logger.warning("WARNING: Risk engine weights do not sum to 100.0!")
    else:
        logger.info("Risk engine weight calibration verified (Total = 100.0).")

    # Initialize SQLite database tables
    from app.core.database import init_db
    init_db()
    logger.info("Database initialized successfully at %s", settings.DATABASE_URL)

    yield

    logger.info("Shutting down %s...", settings.PROJECT_NAME)


def create_application() -> FastAPI:
    """Application factory for FastAPI instance."""
    # Ensure tables are initialized
    from app.core.database import init_db
    init_db()

    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description=(
            "A local-first, defensive cybersecurity platform for static email risk assessment, "
            "explainable machine learning triage, stylometric AI-authorship identification, "
            "and self-directed adversarial evaluation."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # CORS Middleware Configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Centralized Error Handlers
    register_error_handlers(app)

    # Mount API Router under prefix (/api)
    app.include_router(api_router, prefix=settings.API_PREFIX)

    @app.get("/", tags=["Root"])
    async def root_info() -> dict:
        """Root status and discovery payload."""
        return {
            "name": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "docs": "/docs",
            "api_health": f"{settings.API_PREFIX}/health",
            "safety_mode": "defensive-static-only",
        }

    return app


app = create_application()
