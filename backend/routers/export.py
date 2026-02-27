from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional
from backend.services.session import session_service
from backend.services.pdf_export import export_session_pdf
from backend.core.logger import logger

router = APIRouter(prefix="/export-pdf", tags=["Export"])


class ExportRequest(BaseModel):
    session_id: str
    patient_age: Optional[int] = None
    patient_sex: Optional[str] = None


@router.post("")
async def export_pdf(req: ExportRequest):
    """Export the session conversation as a professional PDF report."""
    history = session_service.get_history(req.session_id)
    if not history:
        raise HTTPException(status_code=404, detail="No session data to export")
    try:
        pdf_bytes = export_session_pdf(
            session_history=history,
            patient_info={"age": req.patient_age, "sex": req.patient_sex},
        )
        logger.info(f"PDF exported for session {req.session_id} — {len(pdf_bytes)} bytes")
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="nemesis_{req.session_id}.pdf"'
            },
        )
    except Exception as e:
        logger.error(f"PDF export error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
