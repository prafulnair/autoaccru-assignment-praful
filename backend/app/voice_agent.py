# app/voice_agent.py
import os
from io import BufferedReader
import requests
from fastapi import UploadFile
from dotenv import load_dotenv
import certifi
import io

load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
# Use the base STT endpoint (NOT the /convert one)
ELEVENLABS_STT_URL = "https://api.elevenlabs.io/v1/speech-to-text"

def transcribe_audio_data(file: UploadFile) -> str:
    """
    Send uploaded audio file to ElevenLabs STT and return transcribed text.
    """
    if not ELEVENLABS_API_KEY:
        raise ValueError("Missing ELEVENLABS_API_KEY")

    # Reset file pointer just in case
    if hasattr(file.file, "seek"):
        try:
            file.file.seek(0)
        except Exception:
            pass

    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Accept": "application/json",
    }
    audio_bytes = file.file.read()
    if not audio_bytes:
        raise RuntimeError("Empty audio file received from frontend")

    files = {
        "file": ("recording.webm", io.BytesIO(audio_bytes), "audio/webm")
    }

    data = {
        "model_id": "scribe_v1",
        # Optional toggles:
        # "diarize": "false",
        # "tag_audio_events": "false",
        # "timestamps_granularity": "word",  # or "none"
        # "language_code": "eng",           # let auto-detect if omitted
    }

    try:
        resp = requests.post(
            ELEVENLABS_STT_URL,
            headers=headers,
            files=files,
            data=data,
            timeout=90,
            verify=certifi.where(),  # proper SSL verification
        )
        print("DEBUG response:", resp.status_code, resp.text)
        # Helpful debug on failure
        if resp.status_code >= 400:
            print("ElevenLabs STT error:", resp.status_code, resp.text)
        resp.raise_for_status()
        result = resp.json()
        return (result.get("text") or "").strip()
    except requests.exceptions.RequestException as e:
        # Show server’s body if present
        body = getattr(e.response, "text", None)
        print("ElevenLabs STT request failed:", e, "\nBody:", body)
        raise RuntimeError("Failed to transcribe audio")