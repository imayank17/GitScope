from fastapi import FastAPI
from app.core.config import settings
from app.routers import github
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="GitHub Repository Analytics Platform"
)


@app.get("/")
def root():
    return {
       "application": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "debug": settings.DEBUG,
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }

app.include_router(github.router)