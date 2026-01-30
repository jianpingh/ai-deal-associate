from fastapi import FastAPI, Depends, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select
from typing import List, Optional
from dotenv import load_dotenv
import httpx
import os
import json
import traceback

# Load environment variables from .env file
load_dotenv()

print("INFO: Starting AI Deal Associate API...")

# Import database session and models
# Note: In a real project, use absolute imports assuming 'backend' is in PYTHONPATH check logic
# But for typical simplified structure inside backend/:
try:
    from api.database import get_session, engine
    from api.models import Deal, Asset
    print("INFO: Database modules imported successfully")
except Exception as e:
    print(f"ERROR: Failed to import database modules: {e}")
    traceback.print_exc()
    # Create dummy functions so app can still start
    def get_session():
        raise HTTPException(status_code=503, detail="Database not available")
    engine = None
    Deal = None
    Asset = None

app = FastAPI(title="AI Deal Associate API", version="1.0.0")

# CORS Configuration
# Allow frontend origins from environment variable or use defaults
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "").split(",") if os.getenv("ALLOWED_ORIGINS") else []
DEFAULT_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    # Vercel production domain
    "https://ai-deal-associate-u8hv.vercel.app",
    # Vercel preview domains
    "https://ai-deal-associate-u8hv-*.vercel.app",
]
ALL_ORIGINS = list(set(DEFAULT_ORIGINS + ALLOWED_ORIGINS))

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALL_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# LangGraph API Configuration (read from environment variables)
LANGGRAPH_API_URL = os.getenv("LANGGRAPH_API_URL")
LANGGRAPH_API_KEY = os.getenv("LANGGRAPH_API_KEY")
LANGGRAPH_ASSISTANT_ID = os.getenv("LANGGRAPH_ASSISTANT_ID", "agent")

@app.get("/")
def read_root():
    return {"message": "Welcome to AI Deal Associate API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

# --- Deal Endpoints ---

@app.post("/deals/", response_model=Deal)
def create_deal(deal: Deal, session: Session = Depends(get_session)):
    session.add(deal)
    session.commit()
    session.refresh(deal)
    return deal

@app.get("/deals/", response_model=List[Deal])
def read_deals(
    offset: int = 0, 
    limit: int = Query(default=100, le=100), 
    session: Session = Depends(get_session)
):
    deals = session.exec(select(Deal).offset(offset).limit(limit)).all()
    return deals

@app.get("/deals/{deal_id}", response_model=Deal)
def read_deal(deal_id: int, session: Session = Depends(get_session)):
    deal = session.get(Deal, deal_id)
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    return deal

# --- Asset Endpoints ---

@app.post("/assets/", response_model=Asset)
def create_asset(asset: Asset, session: Session = Depends(get_session)):
    session.add(asset)
    session.commit()
    session.refresh(asset)
    return asset

@app.get("/deals/{deal_id}/assets/", response_model=List[Asset])
def read_deal_assets(deal_id: int, session: Session = Depends(get_session)):
    # Since we removed Foreign Keys, we just query by the integer column
    statement = select(Asset).where(Asset.deal_id == deal_id)
    assets = session.exec(statement).all()
    return assets


# ============================================================
# LangGraph API Proxy Endpoints
# ============================================================

def get_langgraph_headers():
    """Get LangGraph API request headers"""
    return {
        "x-api-key": LANGGRAPH_API_KEY,
        "Content-Type": "application/json",
    }


@app.post("/api/langgraph/threads")
async def create_thread():
    """Create a new conversation thread"""
    # trust_env=False prevents checking for proxies which often causes issues with localhost interaction
    async with httpx.AsyncClient(trust_env=False) as client:
        response = await client.post(
            f"{LANGGRAPH_API_URL}/threads",
            headers=get_langgraph_headers(),
            json={},  # LangGraph API requires an empty JSON body
        )
        response.raise_for_status()
        return response.json()


@app.get("/api/langgraph/threads/{thread_id}/state")
async def get_thread_state(thread_id: str):
    """Get thread state"""
    async with httpx.AsyncClient(trust_env=False) as client:
        response = await client.get(
            f"{LANGGRAPH_API_URL}/threads/{thread_id}/state",
            headers=get_langgraph_headers(),
        )
        response.raise_for_status()
        return response.json()


@app.post("/api/langgraph/threads/{thread_id}/state")
async def update_thread_state(thread_id: str, request: Request):
    """Update thread state"""
    body = await request.json()
    async with httpx.AsyncClient(trust_env=False) as client:
        response = await client.post(
            f"{LANGGRAPH_API_URL}/threads/{thread_id}/state",
            headers=get_langgraph_headers(),
            json=body,
        )
        response.raise_for_status()
        return response.json()


@app.post("/api/langgraph/threads/{thread_id}/runs")
async def create_run(thread_id: str, request: Request):
    """Create a run"""
    body = await request.json()
    body["assistant_id"] = body.get("assistant_id", LANGGRAPH_ASSISTANT_ID)
    
    async with httpx.AsyncClient(trust_env=False) as client:
        response = await client.post(
            f"{LANGGRAPH_API_URL}/threads/{thread_id}/runs",
            headers=get_langgraph_headers(),
            json=body,
        )
        response.raise_for_status()
        return response.json()


@app.post("/api/langgraph/threads/{thread_id}/runs/wait")
async def wait_for_run(thread_id: str, request: Request):
    """Wait for run to complete"""
    body = await request.json()
    body["assistant_id"] = body.get("assistant_id", LANGGRAPH_ASSISTANT_ID)
    
    async with httpx.AsyncClient(timeout=300.0, trust_env=False) as client:  # 5 minute timeout
        response = await client.post(
            f"{LANGGRAPH_API_URL}/threads/{thread_id}/runs/wait",
            headers=get_langgraph_headers(),
            json=body,
        )
        response.raise_for_status()
        return response.json()


@app.post("/api/langgraph/threads/{thread_id}/runs/stream")
async def stream_run(thread_id: str, request: Request):
    """Stream run"""
    body = await request.json()
    body["assistant_id"] = body.get("assistant_id", LANGGRAPH_ASSISTANT_ID)
    
    async def generate():
        async with httpx.AsyncClient(timeout=300.0, trust_env=False) as client:
            async with client.stream(
                "POST",
                f"{LANGGRAPH_API_URL}/threads/{thread_id}/runs/stream",
                headers=get_langgraph_headers(),
                json=body,
            ) as response:
                response.raise_for_status()
                async for chunk in response.aiter_text():
                    yield chunk
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@app.get("/api/langgraph/assistants")
async def get_assistants():
    """Get available assistants"""
    async with httpx.AsyncClient(trust_env=False) as client:
        response = await client.post(
            f"{LANGGRAPH_API_URL}/assistants/search",
            headers=get_langgraph_headers(),
            json={},
        )
        response.raise_for_status()
        return response.json()
