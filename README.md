Dentist Voice Agent – Take‑Home Assessment

A minimal, end‑to‑end prototype of a dentist “voice intake” flow. Patients can be added by speaking their details; the app persists them and shows a simple table + detail dialog.

⸻

What this demo does
	•	Patient list UI: simple table (Shadcn) showing first/last name, phone, and New/Returning status.
	•	Detail dialog: click a row → compact dialog with ID, phone, address, status.
	•	Voice intake: mic → audio file → ElevenLabs STT (scribe_v1) → Gemini parsing → structured patient → DB row.
	•	New vs Returning: marks a patient as returning when the phone number already exists; else new.
	•	SQLite persistence: patients.db, created on first run.

⸻

Tech stack

Backend: Python, FastAPI, SQLAlchemy, SQLite, Pydantic v2, requests, python-dotenv
AI: ElevenLabs Speech‑to‑Text API (model: scribe_v1) + Google Gemini for field extraction
Frontend: React (Vite), Tailwind, Shadcn UI components, Axios

⸻

Run locally

1) Backend

cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# create .env with your keys
cat > .env << 'EOF'
ELEVENLABS_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
EOF
uvicorn app.main:app --reload

API runs at http://localhost:8000. DB file (patients.db) will be created on startup.

2) Frontend

cd frontend
npm install
npm run dev

App runs at http://localhost:5173.

⸻

API overview (used by the UI)

GET /patients

Returns all patients ordered by newest first.

[
  {"id":1,"first_name":"Alice","last_name":"Nguyen","phone_number":"5145731111","address":"100 King St W, Toronto","new_patient":true}
]

GET /patients/{id}

Fetch one patient by ID (used by the dialog on row click).

POST /patients

Creates a patient (manual seed / non‑voice path).

{"first_name":"Mason","last_name":"Patel","phone_number":"4375550101","address":"250 Queen St E, Brampton, ON"}

POST /voice-input

Accepts multipart/form‑data with field file (browser microphone blob). Flow:
	1.	Send audio to ElevenLabs: POST https://api.elevenlabs.io/v1/speech-to-text with model_id=scribe_v1.
	2.	Parse the transcript with Gemini to extract: first_name, last_name, phone_number, address.
	3.	Normalize phone to digits-only and check DB:
	•	If a record with the same phone exists → mark new_patient = false and return that row.
	•	Else create a new row with new_patient = true.
	4.	Returns the final patient JSON.

Note: For demo convenience, if some fields are missing, the endpoint stores a minimal fallback record (e.g., "Unknown", "N/A") so the UI still reflects the action. This can be disabled in app/main.py.

⸻

How “new vs returning” is determined
	•	Voice path (/voice-input): looks up by phone number (digits only). Existing → new_patient=false; new phone → true.

⸻

Quick data addition (optional)

Insert a sample patient:

curl -X POST http://localhost:8000/patients \
  -H 'Content-Type: application/json' \
  -d '{"first_name":"Mason","last_name":"Patel","phone_number