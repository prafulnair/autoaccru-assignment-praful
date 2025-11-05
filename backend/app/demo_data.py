"""Seed data helpers for demos and tests."""

from __future__ import annotations

from typing import Iterable, List

from sqlalchemy.orm import Session

from . import crud, schemas

# Representative patient records (normalized phone numbers).
DEMO_PATIENTS: List[dict[str, str]] = [
    {
        "first_name": "Alice",
        "last_name": "Nguyen",
        "phone_number": "5145550100",
        "address": "123 Maple Avenue, Montreal, QC",
    },
    {
        "first_name": "Benjamin",
        "last_name": "Clark",
        "phone_number": "4385550101",
        "address": "77 Crescent Street, Montreal, QC",
    },
    {
        "first_name": "Sofia",
        "last_name": "Martinez",
        "phone_number": "4385550102",
        "address": "902 Sherbrooke Ouest, Montreal, QC",
    },
]


def build_patient_payload(**overrides: str) -> schemas.PatientCreate:
    """Return a PatientCreate populated with demo defaults and overrides."""

    payload = DEMO_PATIENTS[0].copy()
    payload.update(overrides)
    return schemas.PatientCreate(**payload)


def seed_demo_patients(db: Session, patients: Iterable[dict[str, str]] | None = None):
    """Persist demo patients, returning ORM rows in insertion order."""

    records = []
    to_seed = list(patients) if patients is not None else DEMO_PATIENTS
    for payload in to_seed:
        patient_in = schemas.PatientCreate(**payload)
        records.append(crud.create_patient(db, patient_in))
    return records
