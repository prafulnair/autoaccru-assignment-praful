from pydantic import BaseModel
from typing import Optional

class PatientBase(BaseModel):
    first_name : str
    last_name : str
    phone_number: str
    address : str

class PatientCreate(PatientBase):
    pass 

class Patient(PatientBase):
    id: int
    new_patient: bool

    model_config = {"from_attributes": True}

 