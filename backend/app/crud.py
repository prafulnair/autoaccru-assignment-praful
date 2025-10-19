from sqlalchemy.orm import Session
from . import models, schemas


def list_patients(db: Session):
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
    return (
        db.query(models.PatientTable)
        .filter(models.PatientTable.id == patient_id)
        .first()
    )


def create_patient(db: Session, patient_in: schemas.PatientCreate):
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
    return db.query(models.PatientTable).filter(models.PatientTable.phone_number == phone).first()