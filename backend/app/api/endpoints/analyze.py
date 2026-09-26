"""Email Analysis Endpoint

Accepts email payloads as JSON or file uploads and returns full multi-signal triage telemetry.
"""

from typing import Optional
from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.email import EmailAnalysisInput
from app.schemas.analysis import FullAnalysisResponse
from app.services.triage_service import triage_service
from app.core.errors import ParsingError

router = APIRouter(tags=["Analysis Engine"])


@router.post("/analyze", response_model=FullAnalysisResponse, status_code=status.HTTP_200_OK)
async def analyze_email_json(
    payload: EmailAnalysisInput,
    db: Session = Depends(get_db),
) -> FullAnalysisResponse:
    """Performs static analysis on an email supplied via JSON raw text."""
    if not payload.raw_email or not payload.raw_email.strip():
        raise ParsingError("Email content cannot be empty.")

    return triage_service.analyze_email(
        raw_email=payload.raw_email,
        file_name=payload.file_name,
        db=db,
    )


@router.post("/analyze/upload", response_model=FullAnalysisResponse, status_code=status.HTTP_200_OK)
async def analyze_email_upload(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> FullAnalysisResponse:
    """Performs static analysis on an uploaded .eml or .txt email file."""
    content_bytes = await file.read()
    if not content_bytes:
        raise ParsingError("Uploaded file is empty.")

    raw_text = content_bytes.decode("utf-8", errors="replace")

    return triage_service.analyze_email(
        raw_email=raw_text,
        file_name=file.filename,
        db=db,
    )
