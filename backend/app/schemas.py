from pydantic import BaseModel
from typing import Optional


"""
Pydantic schemas for request/response payloads.

These models define the API contract and are used by FastAPI for
validation and serialization. They mirror the ORM model fields while
controlling which attributes appear on create vs. read.
"""

class PatientBase(BaseModel):
    """
    Shared fields for patient payloads.

    Attributes:
        first_name: Patient's given name.
        last_name: Patient's family name.
        phone_number: Normalized phone (digits-only, handled upstream).
        address: Street/mailing address.
    """
    first_name : str
    last_name : str
    phone_number: str
    address : str

class PatientCreate(PatientBase):
    """
    Payload for creating a patient record.

    Inherits all fields from PatientBase. Server logic determines the
    `new_patient` flag; clients do not send it on create.
    """
    pass 

class Patient(PatientBase):
    """
    Read model returned by the API.

    Attributes:
        id: Database primary key.
        new_patient: True on first intake, False on subsequent visits.

    Notes:
        `model_config.from_attributes=True` enables Pydantic v2 to
        construct this schema directly from SQLAlchemy ORM instances.
    """
    id: int
    new_patient: bool

    model_config = {"from_attributes": True}

 