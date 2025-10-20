from sqlalchemy.orm import Session
from . import models, schemas


def list_patients(db: Session):
    """Return all patients ordered by newest first.

    Args:
    db: Active SQLAlchemy session.

    Returns:
    list[models.PatientTable]: Patient rows sorted by id DESC.
    """
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
    """Find a patient by exact (first_name, last_name, phone_number).

    Assumes the phone number is already normalized upstream.

    Args:
        db: Active SQLAlchemy session.
        first_name: Patient first name (exact match).
        last_name: Patient last name (exact match).
        phone_number: Normalized phone (exact match).

    Returns:
        models.PatientTable | None: Matching row if found, else None.
    """
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
    """Fetch a single patient by primary key.

    Args:
        db: Active SQLAlchemy session.
        patient_id: Auto-increment integer id.

    Returns:
        models.PatientTable | None: Matching row if found, else None.
    """
    return (
        db.query(models.PatientTable)
        .filter(models.PatientTable.id == patient_id)
        .first()
    )


def create_patient(db: Session, patient_in: schemas.PatientCreate):
    """Create a patient and set `new_patient` based on prior existence.

    Uses `get_patient_by_identity` to determine if this exact identity already
    exists. If not found, marks the new record as `new_patient=True`, otherwise
    `False`. Persists the row and refreshes it.

    Args:
        db: Active SQLAlchemy session.
        patient_in: Validated patient payload (expects normalized phone).

    Returns:
        models.PatientTable: The persisted ORM object (with id populated).
    """
    existing = get_patient_by_identity(
        db,
        patient_in.first_name,
        patient_in.last_name,
        patient_in.phone_number,
    )
    is_new = existing is None

    obj = models.PatientTable(
        first_name=patient_in.first_name,
        last_name=patient_in.last_name,
        phone_number=patient_in.phone_number,
        address=patient_in.address,
        new_patient=is_new,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def get_patient_by_phone(db: Session, phone: str):
    """Find a patient by normalized phone number.

    Args:
    db: Active SQLAlchemy session.
    phone: Normalized phone (digits-only, e.g., '5145737122').

    Returns:
    models.PatientTable | None: Matching row if found, else None.
    """
    return db.query(models.PatientTable).filter(models.PatientTable.phone_number == phone).first()