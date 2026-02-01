"""
LangGraph API Proxy Routes

Proxy endpoints for LangGraph Cloud API.
These endpoints return raw LangGraph responses to maintain SDK compatibility.
"""

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
import httpx

from core.config import settings


router = APIRouter(prefix="/api/langgraph", tags=["LangGraph"])


def get_langgraph_headers() -> dict:
    """Get LangGraph API request headers"""
    return {
        "x-api-key": settings.LANGGRAPH_API_KEY,
        "Content-Type": "application/json",
    }


@router.post("/threads", summary="Create thread")
async def create_thread():
    """Create a new conversation thread"""
    async with httpx.AsyncClient(trust_env=False) as client:
        response = await client.post(
            f"{settings.LANGGRAPH_API_URL}/threads",
            headers=get_langgraph_headers(),
            json={},
        )
        response.raise_for_status()
        return response.json()


@router.get("/threads/{thread_id}/state", summary="Get thread state")
async def get_thread_state(thread_id: str):
    """Get thread state"""
    async with httpx.AsyncClient(trust_env=False) as client:
        response = await client.get(
            f"{settings.LANGGRAPH_API_URL}/threads/{thread_id}/state",
            headers=get_langgraph_headers(),
        )
        response.raise_for_status()
        return response.json()


@router.post("/threads/{thread_id}/state", summary="Update thread state")
async def update_thread_state(thread_id: str, request: Request):
    """Update thread state"""
    body = await request.json()
    async with httpx.AsyncClient(trust_env=False) as client:
        response = await client.post(
            f"{settings.LANGGRAPH_API_URL}/threads/{thread_id}/state",
            headers=get_langgraph_headers(),
            json=body,
        )
        response.raise_for_status()
        return response.json()


@router.post("/threads/{thread_id}/runs", summary="Create run")
async def create_run(thread_id: str, request: Request):
    """Create a run"""
    body = await request.json()
    body["assistant_id"] = body.get("assistant_id", settings.LANGGRAPH_ASSISTANT_ID)
    
    async with httpx.AsyncClient(trust_env=False) as client:
        response = await client.post(
            f"{settings.LANGGRAPH_API_URL}/threads/{thread_id}/runs",
            headers=get_langgraph_headers(),
            json=body,
        )
        response.raise_for_status()
        return response.json()


@router.post("/threads/{thread_id}/runs/wait", summary="Wait for run")
async def wait_for_run(thread_id: str, request: Request):
    """Wait for run to complete"""
    body = await request.json()
    body["assistant_id"] = body.get("assistant_id", settings.LANGGRAPH_ASSISTANT_ID)
    
    async with httpx.AsyncClient(timeout=300.0, trust_env=False) as client:
        response = await client.post(
            f"{settings.LANGGRAPH_API_URL}/threads/{thread_id}/runs/wait",
            headers=get_langgraph_headers(),
            json=body,
        )
        response.raise_for_status()
        return response.json()


@router.post("/threads/{thread_id}/runs/stream", summary="Stream run")
async def stream_run(thread_id: str, request: Request):
    """Stream run with Server-Sent Events"""
    body = await request.json()
    body["assistant_id"] = body.get("assistant_id", settings.LANGGRAPH_ASSISTANT_ID)
    
    async def generate():
        async with httpx.AsyncClient(timeout=300.0, trust_env=False) as client:
            async with client.stream(
                "POST",
                f"{settings.LANGGRAPH_API_URL}/threads/{thread_id}/runs/stream",
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


@router.get("/assistants", summary="Get assistants")
async def get_assistants():
    """Get available assistants"""
    async with httpx.AsyncClient(trust_env=False) as client:
        response = await client.post(
            f"{settings.LANGGRAPH_API_URL}/assistants/search",
            headers=get_langgraph_headers(),
            json={},
        )
        response.raise_for_status()
        return response.json()
