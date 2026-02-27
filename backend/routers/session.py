from fastapi import APIRouter, HTTPException
from backend.services.session import session_service

router = APIRouter(prefix="/history", tags=["Session"])


@router.get("/{session_id}")
async def get_history(session_id: str):
    history = session_service.get_history(session_id)
    if not history:
        raise HTTPException(status_code=404, detail="Session not found or empty")
    return {"session_id": session_id, "turns": history}


@router.delete("/{session_id}")
async def clear_history(session_id: str):
    session_service.clear(session_id)
    return {"message": f"Session {session_id} cleared"}
