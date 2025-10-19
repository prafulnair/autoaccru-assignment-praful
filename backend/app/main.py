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
    try:
        # First, Transcribe voice data
        transcribed_text = transcribe_audio_data(file)
        print("Transcribed text:\n", transcribed_text)

        # Then Use Gemini (or parser) to extract patient information
        parsed = parse_patient_details(transcribed_text)
        print("Parsed fields:", parsed)

    except Exception as e:
        print("Error during transcription or parsing:", e)
        raise HTTPException(status_code=500, detail=f"Internal processing error: {str(e)}")

    # now we haev to validate the parsed data
    first_name = parsed.get("first_name")
    last_name = parsed.get("last_name")

    # check if the patient exist in the database, if yes, , ask for patient id unique to the patient, if patient id matches, its existing patient
    # then change the new_patient boolean to false. 

    phone = parsed.get("phone_number")
    address = parsed.get("address")
        
    # Check if patient already exists (by phone number)
    existing_patient = crud.get_patient_by_phone(db, phone)

    if existing_patient:
        # Returning patient
        existing_patient.new_patient = False
        db.commit()
        db.refresh(existing_patient)
        return existing_patient

    if not all([first_name, last_name, phone, address]):
            # For demo purposes, still store partial data so frontend sees success
            fallback_patient = schemas.PatientCreate(
                first_name=first_name or "Unknown",
                last_name=last_name or "Unknown",
                phone_number=phone or "N/A",
                address=address or "N/A"
            )
            new_patient = crud.create_patient(db, fallback_patient)
            print(" Partial data detected; stored fallback patient.")
            return new_patient

    
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
