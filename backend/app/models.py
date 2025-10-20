from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base

Base = declarative_base()

"""
SQLAlchemy ORM models for the Dentist Voice Agent.

Defines the single `patients` table used by the application.
"""


class PatientTable(Base):
    """
    SQLAlchemy ORM model for the `patients` table.

    Columns:
        id (Integer): Primary key.
        first_name (String): Patient's given name (required).
        last_name (String): Patient's family name (required).
        phone_number (String): Normalized phone (digits-only) used for dedup (required).
        address (String): Mailing/street address (required).
        new_patient (Boolean): True on first intake, set to False on subsequent visits.
    """
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    address = Column(String, nullable=False)
    new_patient = Column(Boolean, nullable=False, default=True)



