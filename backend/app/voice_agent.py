import requests
from fastapi import UploadFile
import os
from dotenv import load_dotenv


load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_STT_URL = "https://api.elevenlabs.io/v1/speech-to-text/convert"

def transcribe_audio_data(file: UploadFile) -> str:
    """
    Send uploaded audio data/ file to the api and return transcribed text.
    """

    if not ELEVENLABS_API_KEY:
        raise ValueError("MIssing API_KEY environmental variable")
    
    headers = {
        "xi-api-key":  ELEVENLABS_API_KEY
    }
    files = {
        "file": (file.filename, file.file, file.content_type)
    }

    data = {
        "model_id": "scribe_v1",
        "diarize": "false",
        "timestamps_granularity": "word"
    }

    # gracefully handle data transmission
    try:
        response = requests.post(ELEVENLABS_STT_URL, headers=headers, files=files, data=data)
        response.raise_for_status()
        result = response.json()

        # we get transcribed text under 'text' key
        return result.get("text", "").strip()
    except Exception as e:
        print("Something went wrong while transcribing the audio data: ", e)
        raise RuntimeError("Filed to transcribe audio")
    
    