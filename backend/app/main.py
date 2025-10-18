from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from .voice_agent import transcribe_audio_data 
from .ai_parser import parse_patient_details

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
    Receive audio file -> transcribe via ElevenLabs -> parse via Gemini -> 
    store patient.

    """
    # first, transcribe the voice data
    transcribed_text = transcribe_audio_data(file)
    
    # second, use Gemini to extract patient information
    parsed = parse_patient_details(transcribed_text)

    # now we haev to validate the parsed data
    first_name = parsed.get("first_name")
    last_name = parsed.get("last_name")
    phone = parsed.get("phone_number")
    address = parsed.get("address")

    if not all([first_name, last_name, phone, address]):
        raise HTTPException(
            status_code= 400,
            detail={
                "error": "Could not extract all required details from the audio. Please try again",
                "parsed_result":parsed,
                "transcribed_text": transcribed_text
            }
        )
    
    # if everythign is good (data is complete and valid)
    # move in with Persistance
    patient_in = schemas.PatientCreate(
        first_name=first_name,
        last_name=last_name,
        phone_number=phone,
        address=address
    )

    new_patient = crud.create_patient(db, patient_in)
    return new_patient

    ...