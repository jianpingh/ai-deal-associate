"""
AI Deal Associate API

Main application entry point with layered architecture.
"""

import sys
import traceback
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from core.config import settings
from schemas import Response, ErrorCode

# Lazy load database to avoid startup crashes
_db_initialized = False


def _init_database():
    """Initialize database connection lazily"""
    global _db_initialized
    if _db_initialized:
        return True
    try:
        from db.database import init_db
        init_db()
        _db_initialized = True
        print("INFO: Database initialized successfully", flush=True)
        return True
    except Exception as e:
        print(f"ERROR: Failed to initialize database: {e}", flush=True)
        traceback.print_exc()
        return False


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    print("INFO: Starting AI Deal Associate API...", flush=True)
    print(f"INFO: Python version: {sys.version}", flush=True)
    
    # Attempt database initialization (non-blocking)
    _init_database()
    
    yield
    
    print("INFO: Shutting down AI Deal Associate API...", flush=True)


# OpenAPI Tags for documentation
tags_metadata = [
    {
        "name": "Health",
        "description": "Health check and root endpoints",
    },
    {
        "name": "Deals",
        "description": "Deal management operations",
    },
    {
        "name": "Assets",
        "description": "Asset management operations",
    },
    {
        "name": "Users",
        "description": "User management operations",
    },
    {
        "name": "LangGraph",
        "description": "LangGraph API proxy - AI conversation endpoints",
    },
]

# Custom OpenAPI responses for unified format
custom_responses = {
    422: {
        "description": "Validation Error",
        "content": {
            "application/json": {
                "example": {
                    "code": 400,
                    "msg": "Validation error",
                    "data": [
                        {"loc": ["body", "name"], "msg": "field required", "type": "value_error.missing"}
                    ]
                }
            }
        }
    }
}

# Create FastAPI application
app = FastAPI(
    title="AI Deal Associate API",
    version="1.0.0",
    description="Real estate deal analysis API powered by LangGraph",
    lifespan=lifespan,
    responses=custom_responses,
    openapi_tags=tags_metadata,
)


# ============================================================
# Exception Handlers
# ============================================================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with unified response format"""
    return JSONResponse(
        status_code=200,
        content=Response.error(
            code=ErrorCode.PARAM_ERROR,
            msg="Validation error",
            data=exc.errors()
        ).model_dump()
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors with unified response format"""
    # Skip for LangGraph proxy endpoints (they return raw responses)
    if request.url.path.startswith("/api/langgraph"):
        raise exc
    
    return JSONResponse(
        status_code=200,
        content=Response.error(
            code=ErrorCode.SERVER_ERROR,
            msg=str(exc)
        ).model_dump()
    )


# ============================================================
# CORS Middleware
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# Include Routers
# ============================================================

from api.routes import deals_router, assets_router, users_router, langgraph_router

app.include_router(deals_router)
app.include_router(assets_router)
app.include_router(users_router)
app.include_router(langgraph_router)


# ============================================================
# Root Endpoints
# ============================================================

@app.get("/", tags=["Health"])
def read_root():
    """Root endpoint - returns welcome message"""
    return Response.success(data={"message": "Welcome to AI Deal Associate API"})


@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint"""
    db_status = "connected" if _db_initialized else "not_initialized"
    return Response.success(data={
        "status": "ok",
        "database": db_status
    })
