from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.workflow_router import router as workflow_router
from app.api.v1.agent_router import router as agent_router
from app.api.v1.webhook_router import router as webhook_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="NEXORA AI - Enterprise AI Automation Platform",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routers
app.include_router(
    workflow_router,
    prefix=settings.API_V1_STR,
    tags=["Workflows"],
)

app.include_router(
    agent_router,
    prefix=settings.API_V1_STR,
    tags=["Agents"],
)

app.include_router(
    webhook_router,
    prefix=settings.API_V1_STR,
    tags=["Webhooks"],
)


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Welcome to NEXORA AI",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": "1.0.0",
    }
