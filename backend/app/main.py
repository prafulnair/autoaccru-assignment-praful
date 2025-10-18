from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from .voice_agent import transcribe_audio_data 

from .database import init_db, get_db

from . import crud, schemas

app = FastAPI(title="Dentist Voice Agent")

# Resolve CORS, allow frontend to call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    init_db()


@app.get("/patients", response_model=List[schemas.Patient])
def get_patients(db: Session = Depends(get_db)):
    return crud.list_patients(db)

@app.post("/patients", response_model=schemas.Patient, status_code=201)
def add_patient(patient: schemas.PatientCreate, db: Session = Depends(get_db)):
    return crud.create_patient(db, patient)


@app.get("/patients/{patient_id}", response_model=schemas.Patient)
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = crud.get_patient_by_id(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

@app.post('/voice-input', response_model=schemas.Patient, status_code=201)
def voice_input(file: UploadFile  = File(...), db: Session = Depends(get_db)):
    """
    Recv audio file (Data) -> transcribes it using 11_labs, extract patient info
    and creates / returns a patiennt record
    """

    ...