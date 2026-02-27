from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from backend.services.inference import inference_service
from backend.services.session import session_service
from backend.core.logger import logger

router = APIRouter(prefix="/analyze", tags=["Analysis"])


class AnalyzeRequest(BaseModel):
    session_id: str = Field(..., description="Unique session identifier")
    symptoms: str = Field(..., min_length=5, description="Patient symptoms description")
    patient_age: Optional[int] = Field(None, ge=0, le=120)
    patient_sex: Optional[str] = Field(None, pattern="^(male|female|other)$")


class AnalyzeResponse(BaseModel):
    session_id: str
    full_response: str
    reasoning: str
    differentials: str
    workup: str
    treatment: str
    red_flags: str


@router.post("", response_model=AnalyzeResponse)
async def analyze(req: AnalyzeRequest):
    """
    Run clinical reasoning on the provided symptoms.
    Returns structured output including chain-of-thought reasoning,
    differential diagnoses, recommended workup, and treatment plan.
    """
    logger.info(f"[{req.session_id}] Analyzing: {req.symptoms[:80]}...")
    try:
        history = session_service.get_chat_pairs(req.session_id)
        result = inference_service.analyze(
            symptoms=req.symptoms,
            patient_age=req.patient_age,
            patient_sex=req.patient_sex,
            history=history if history else None,
        )
        # Persist turn
        session_service.add_turn(req.session_id, "user", req.symptoms)
        session_service.add_turn(req.session_id, "assistant", result["full_response"])

        return AnalyzeResponse(session_id=req.session_id, **result)
    except Exception as e:
        logger.error(f"Inference error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
