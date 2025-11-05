"""CRUD helpers for patient data."""

from __future__ import annotations

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from . import models, schemas


def list_patients(db: Session):
    """Return all patients ordered by newest first."""
    return (
        db.query(models.PatientTable)
        .order_by(models.PatientTable.id.desc())
        .all()
    )


def get_patient_by_identity(
    db: Session,
    first_name: str,
    last_name: str,
    phone_number: str,
):
    """Find a patient by exact (first_name, last_name, phone_number)."""
    return (
        db.query(models.PatientTable)
        .filter(
            models.PatientTable.first_name == first_name,
            models.PatientTable.last_name == last_name,
            models.PatientTable.phone_number == phone_number,
        )
        .first()
    )


def get_patient_by_id(db: Session, patient_id: int):
    """Fetch a single patient by primary key."""
    return (
        db.query(models.PatientTable)
        .filter(models.PatientTable.id == patient_id)
        .first()
    )


def get_patient_by_phone(db: Session, phone: str):
    """Find a patient by normalized phone number."""
    return (
        db.query(models.PatientTable)
        .filter(models.PatientTable.phone_number == phone)
        .first()
    )


def create_patient(db: Session, patient_in: schemas.PatientCreate):
    """Create or update a patient keyed by normalized phone number."""

    existing_by_phone = get_patient_by_phone(db, patient_in.phone_number)
    if existing_by_phone:
        existing_by_phone.first_name = patient_in.first_name
        existing_by_phone.last_name = patient_in.last_name
        existing_by_phone.address = patient_in.address
        existing_by_phone.new_patient = False
        db.add(existing_by_phone)
        db.commit()
        db.refresh(existing_by_phone)
        return existing_by_phone

    obj = models.PatientTable(
        first_name=patient_in.first_name,
        last_name=patient_in.last_name,
        phone_number=patient_in.phone_number,
        address=patient_in.address,
        new_patient=True,
    )
    db.add(obj)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        existing_by_phone = get_patient_by_phone(db, patient_in.phone_number)
        if existing_by_phone:
            existing_by_phone.first_name = patient_in.first_name
            existing_by_phone.last_name = patient_in.last_name
            existing_by_phone.address = patient_in.address
            existing_by_phone.new_patient = False
            db.add(existing_by_phone)
            db.commit()
            db.refresh(existing_by_phone)
            return existing_by_phone
        raise

    db.refresh(obj)
    return obj
