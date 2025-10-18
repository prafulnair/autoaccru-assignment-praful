# Dentist Voice Agent – Take Home Assessment

A simple web app that allows a dental office to manage patients using a voice-enabled workflow.
Built as a prototype using FastAPI, React, SQLite, and Shadcn UI.

---

## Tech Stack

* **Backend:** Python, FastAPI, SQLite, Pydantic
* **Frontend:** React (Vite), Shadcn UI, Axios
* **Voice Agent:** [To be integrated — API-based or stubbed]

---

## Features

* View all patients in a table (name, phone, address, new/returning status)
* Click a patient to view detailed info in a dialog
* Add new patients via voice agent (voice → structured data → DB)
* Detects whether a patient is new or returning (based on existing DB records)

---

## Project Structure

```plaintext
autoaccru-voice-assignment/
├── backend/         # FastAPI backend
│   └── app/
│       ├── main.py
│       ├── models.py
│       ├── crud.py
│       └── database.py
├── frontend/        # React + Vite + Shadcn UI frontend
│   └── src/
│       ├── App.jsx
│       └── components/
├── README.md
└── .gitignore
```

---

## Setup & Run

### 1. Backend (FastAPI)

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

By default, the API will be available at [http://localhost:8000](http://localhost:8000)

### 2. Frontend (React)

```bash
cd frontend
npm install
npm run dev
```

This will start the app at [http://localhost:5173](http://localhost:5173) (or similar).

---

## How It Works

1. **Patient Table:**
   Fetches all patients from backend. Shadcn UI table, click to open dialog.
2. **Voice Agent:**
   Click “Add Patient via Voice”, record details (first name, last name, phone, address).
   [Details to be added based on integrated API.]
3. **New/Returning Detection:**
   Before adding a new patient, checks DB for matching (name + phone).
   Sets `new_patient` accordingly.

---
