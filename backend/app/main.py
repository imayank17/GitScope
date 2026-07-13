from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI

from app.core.config import settings
from app.routers import github


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup ---
    app.state.http_client = httpx.AsyncClient(
        timeout=httpx.Timeout(30.0),     # 30s total timeout
        follow_redirects=True,            # Follow GitHub redirects
    )

    # Automatically create tables in PostgreSQL on startup
    import sqlalchemy as sa
    from app.database import Base
    from app.database.session import engine
    import app.models  # noqa: F401 (Ensure models are registered with Base.metadata)

    async with engine.begin() as conn:
        # Safely expand repositories schema with new columns if they do not exist
        await conn.execute(
            sa.text("ALTER TABLE repositories ADD COLUMN IF NOT EXISTS last_synced_at TIMESTAMP WITH TIME ZONE;")
        )
        await conn.execute(
            sa.text("ALTER TABLE repositories ADD COLUMN IF NOT EXISTS sync_status VARCHAR(50) DEFAULT 'PENDING' NOT NULL;")
        )
        await conn.execute(
            sa.text("ALTER TABLE repositories ADD COLUMN IF NOT EXISTS sync_error TEXT;")
        )
        # Create all tables (including the new repository_snapshots table)
        await conn.run_sync(Base.metadata.create_all)

    yield  # App runs here — handles requests

    # --- Shutdown ---
    await app.state.http_client.aclose()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="GitHub Repository Analytics Platform",
    lifespan=lifespan,
)


#Register Routers-------

app.include_router(github.router)

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
        "status": "healthy",
    }