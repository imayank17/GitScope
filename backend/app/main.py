import time
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware

# Initialize centralized logging immediately on import
from app.core.logging import setup_logging, get_logger
setup_logging()

logger = get_logger("app.main")

from app.core.config import settings
from app.routers import github


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup ---
    logger.info("Application startup sequence initiated.")
    
    app.state.http_client = httpx.AsyncClient(
        timeout=httpx.Timeout(30.0),     # 30s total timeout
        follow_redirects=True,            # Follow GitHub redirects
    )

    # Automatically create tables in PostgreSQL on startup
    import sqlalchemy as sa
    from app.database import Base
    from app.database.session import engine
    import app.models  # noqa: F401 (Ensure models are registered with Base.metadata)

    try:
        async with engine.begin() as conn:
            # Create all tables (including the new repository_snapshots table)
            await conn.run_sync(Base.metadata.create_all)

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
        
        logger.info("Database connected successfully and schema migrations validated.")
    except Exception as e:
        logger.exception("Database connection and schema migration failed during startup lifespan.")
        raise

    logger.info("Application startup complete. Ready to handle requests.")
    yield  # App runs here — handles requests

    # --- Shutdown ---
    logger.info("Application shutdown sequence initiated. Cleaning up HTTP client.")
    await app.state.http_client.aclose()
    logger.info("Application shutdown complete.")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="GitHub Repository Analytics Platform",
    lifespan=lifespan,
)


# HTTP Request/Response Logging Middleware
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()
        
        # Log incoming request (path and method)
        logger.info(f"Incoming Request: {request.method} {request.url.path}")
        
        try:
            response = await call_next(request)
            process_time = (time.perf_counter() - start_time) * 1000
            
            logger.info(
                f"Response: {request.method} {request.url.path} | "
                f"Status: {response.status_code} | "
                f"Duration: {process_time:.2f}ms"
            )
            return response
        except Exception as e:
            process_time = (time.perf_counter() - start_time) * 1000
            logger.exception(
                f"Request Failed: {request.method} {request.url.path} | "
                f"Error: {str(e)} | "
                f"Duration: {process_time:.2f}ms"
            )
            raise


app.add_middleware(LoggingMiddleware)

# CORS — allow the Vite dev server to reach the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handler to log validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(
        f"Request validation error: {request.method} {request.url.path} | "
        f"Detail: {exc.errors()}"
    )
    from fastapi.exception_handlers import request_validation_exception_handler
    return await request_validation_exception_handler(request, exc)


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