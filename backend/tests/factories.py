"""Test factories for patient data."""

from __future__ import annotations

import itertools
from typing import Any, Dict

from sqlalchemy.orm import Session

from app import crud, schemas

_phone_counter = itertools.count(1000)


def next_phone_number() -> str:
    """Return a unique-looking Montreal phone number for testing."""

    suffix = next(_phone_counter)
    return f"514555{suffix:04d}"


def patient_payload(**overrides: Any) -> Dict[str, Any]:
    """Dictionary payload suitable for API requests."""

    payload: Dict[str, Any] = {
        "first_name": "Test",
        "last_name": "Patient",
        "phone_number": next_phone_number(),
        "address": "100 King Street, Montreal, QC",
    }
    payload.update(overrides)
    return payload


def create_patient(db: Session, **overrides: Any):
    """Persist a patient row and return the ORM object."""

    payload = patient_payload(**overrides)
    patient_in = schemas.PatientCreate(**payload)
    return crud.create_patient(db, patient_in)
