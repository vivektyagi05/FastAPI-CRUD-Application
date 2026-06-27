# ============================================================
# main.py
# FastAPI application factory.
# - Registers the tasks router
# - Creates database tables on startup
# - Serves the frontend via Jinja2 templates
# - Configures CORS, exception handlers, and static files
# ============================================================

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import SQLAlchemyError

from app.database import Base, engine
from app.routers import tasks

# ---------------------------------------------------------------------------
# Create all tables (runs once at startup, safe to call repeatedly)
# ---------------------------------------------------------------------------
Base.metadata.create_all(bind=engine)

# ---------------------------------------------------------------------------
# App instance
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Task Manager API",
    description=(
        "A full CRUD REST API built with FastAPI + SQLAlchemy + SQLite. "
        "Demonstrates GET, POST, PUT, PATCH, and DELETE operations."
    ),
    version="1.0.0",
    docs_url="/docs",       # Swagger UI
    redoc_url="/redoc",     # ReDoc
)

# ---------------------------------------------------------------------------
# CORS — allow the HTML frontend (same host, any port in dev)
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Static files & templates
# ---------------------------------------------------------------------------
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ---------------------------------------------------------------------------
# Include routers
# ---------------------------------------------------------------------------
app.include_router(tasks.router)


# ---------------------------------------------------------------------------
# Global exception handlers
# ---------------------------------------------------------------------------

@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """Catch database-level errors and return a tidy 500 JSON response."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "A database error occurred. Please try again.",
            "data": None,
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Fallback handler for unexpected server errors."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "An unexpected error occurred.",
            "data": None,
        },
    )


# ---------------------------------------------------------------------------
# Frontend route — serves the single-page HTML app
# ---------------------------------------------------------------------------

@app.get("/", include_in_schema=False)
async def serve_frontend(request: Request):
    """Serve the Task Manager SPA."""
    return templates.TemplateResponse("index.html", {"request": request})


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.get("/health", tags=["Health"])
async def health_check():
    """Simple liveness probe."""
    return {"status": "ok", "message": "Task Manager API is running"}
