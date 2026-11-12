from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.database.connection import (
    check_mongodb_connection,
    initialize_database,
    close_mongodb_connection,
)

from app.routes import (
    auth,
    users,
    candidates,
    recruiters,
    companies,
    job_offers,
    applications,
    admin,
    dashboard,
    matching,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    initialize_database()
    yield

    # Shutdown
    close_mongodb_connection()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
)


# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(candidates.router)
app.include_router(recruiters.router)
app.include_router(companies.router)
app.include_router(job_offers.router)
app.include_router(applications.router)
app.include_router(admin.router)
app.include_router(dashboard.router)
app.include_router(matching.router)


@app.get("/")
async def root():
    return {
        "message": "Welcome to SmartRecruit API",
        "version": settings.APP_VERSION,
        "status": "running",
    }


@app.get("/health")
async def health():
    try:
        check_mongodb_connection()

        return {
            "status": "healthy",
            "mongodb": "connected",
        }

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "unhealthy",
                "mongodb": "disconnected",
            },
        )