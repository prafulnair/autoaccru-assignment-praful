from __future__ import annotations

import logging
import os
import re
from typing import List

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import crud, schemas
from .ai_parser import parse_patient_details
from .database import get_db, init_db
from .exceptions import ProviderError
from .voice_agent import transcribe_audio_data


def _configure_logging() -> None:
    level_name = os.getenv("BACKEND_LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


def _parse_origins(raw_origins: str | None) -> List[str]:
    if not raw_origins:
        return ["http://localhost:5173"]
    origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]
    return origins or ["http://localhost:5173"]


_configure_logging()
logger = logging.getLogger(__name__)

SETTINGS = {
    "app_title": os.getenv("BACKEND_APP_TITLE", "Dentist Voice Agent"),
    "allow_origins": _parse_origins(os.getenv("BACKEND_ALLOWED_ORIGINS")),
    "allow_credentials": os.getenv("BACKEND_ALLOW_CREDENTIALS", "true").lower() == "true",
    "allow_methods": os.getenv("BACKEND_ALLOW_METHODS", "*").split(","),
    "allow_headers": os.getenv("BACKEND_ALLOW_HEADERS", "*").split(","),
}

app = FastAPI(title=SETTINGS["app_title"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=SETTINGS["allow_origins"],
    allow_credentials=SETTINGS["allow_credentials"],
    allow_methods=[method.strip() or "*" for method in SETTINGS["allow_methods"]],
    allow_headers=[header.strip() or "*" for header in SETTINGS["allow_headers"]],
)


def clean_and_validate(parsed: dict) -> dict:
    """Normalize and minimally validate parsed patient data."""
    for k, v in parsed.items():
        if isinstance(v, str):
            parsed[k] = v.strip() or None

    if parsed.get("phone_number"):
        parsed["phone_number"] = re.sub(r"\D", "", parsed["phone_number"])

    if parsed.get("phone_number") and len(parsed["phone_number"]) < 10:
        parsed["phone_number"] = None

    return parsed


@app.on_event("startup")
def startup_event() -> None:
    """FastAPI startup hook that initializes the database schema."""
    init_db()


@app.get("/patients", response_model=List[schemas.Patient])
def get_patients(db: Session = Depends(get_db)):
    """List all patients ordered by newest first."""
    return crud.list_patients(db)


@app.post("/patients", response_model=schemas.Patient, status_code=201)
def add_patient(patient: schemas.PatientCreate, db: Session = Depends(get_db)):
    """Create a patient record from a structured JSON payload."""
    return crud.create_patient(db, patient)


@app.get("/patients/{patient_id}", response_model=schemas.Patient)
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    """Retrieve a single patient by ID."""
    patient = crud.get_patient_by_id(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@app.post("/voice-input", response_model=schemas.Patient, status_code=201)
def voice_input(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Voice intake endpoint: audio → STT → LLM parsing → persistence."""
    logger.info(
        "voice_input.received",
        extra={
            "event": "voice_input.received",
            "filename": file.filename,
            "content_type": file.content_type,
        },
    )
    try:
        logger.info(
            "voice_input.transcription.start",
            extra={"event": "voice_input.transcription.start", "stage": "transcription"},
        )
        transcribed_text = transcribe_audio_data(file)
        logger.info(
            "voice_input.transcription.success",
            extra={
                "event": "voice_input.transcription.success",
                "stage": "transcription",
                "char_length": len(transcribed_text),
            },
        )

        logger.info(
            "voice_input.parsing.start",
            extra={"event": "voice_input.parsing.start", "stage": "parsing"},
        )
        parsed = parse_patient_details(transcribed_text)
        logger.info(
            "voice_input.parsing.success",
            extra={
                "event": "voice_input.parsing.success",
                "stage": "parsing",
                "fields": sorted(parsed.keys()),
            },
        )

        parsed = clean_and_validate(parsed)
        logger.info(
            "voice_input.validation.success",
            extra={"event": "voice_input.validation.success", "stage": "validation"},
        )

    except ProviderError as exc:
        log_fields = {"event": "voice_input.provider_error", "stage": "external"}
        log_fields.update(exc.to_log_fields())
        logger.error("Provider failure in voice pipeline", extra=log_fields)
        raise HTTPException(
            status_code=502,
            detail={
                "error": "provider_error",
                "provider": exc.provider,
                "message": exc.message,
            },
        ) from exc
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Unexpected failure in voice pipeline", extra={"event": "voice_input.error"})
        raise HTTPException(status_code=500, detail="Internal processing error") from exc

    first_name = parsed.get("first_name")
    last_name = parsed.get("last_name")
    phone = parsed.get("phone_number")
    address = parsed.get("address")

    required_fields = ["first_name", "last_name", "phone_number", "address"]
    missing_fields = [field for field in required_fields if not parsed.get(field)]
    if missing_fields:
        logger.warning(
            "voice_input.validation.incomplete",
            extra={
                "event": "voice_input.validation.incomplete",
                "stage": "validation",
                "missing_fields": missing_fields,
            },
        )
        raise HTTPException(
            status_code=422,
            detail={
                "error": "incomplete_patient_data",
                "missing_fields": missing_fields,
            },
        )

    existing_patient = crud.get_patient_by_phone(db, phone)
    if existing_patient:
        existing_patient.new_patient = False
        db.commit()
        db.refresh(existing_patient)
        logger.info(
            "voice_input.persistence.returning_patient",
            extra={
                "event": "voice_input.persistence.returning_patient",
                "stage": "persistence",
                "patient_id": existing_patient.id,
            },
        )
        return existing_patient

    patient_in = schemas.PatientCreate(
        first_name=first_name,
        last_name=last_name,
        phone_number=phone,
        address=address,
    )

    new_patient = crud.create_patient(db, patient_in)
    logger.info(
        "voice_input.persistence.new_patient",
        extra={
            "event": "voice_input.persistence.new_patient",
            "stage": "persistence",
            "patient_id": new_patient.id,
        },
    )
    return new_patient
