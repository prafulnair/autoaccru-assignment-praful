# backend/app/ai_parser.py
import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("Missing GEMINI_API_KEY in environment")

genai.configure(api_key=GEMINI_API_KEY)


def parse_patient_details(transcribed_text: str) -> dict:
    """
    Uses Gemini to extract structured patient details from the transcribed voice text.
    Returns a dict/json like:
    {
        "first_name": "John",
        "last_name": "Doe",
        "phone_number": "5145737144",
        "address": "1570 Rue Saint Timothée, Montreal"
    }
    """
    model = genai.GenerativeModel(
        model_name=GEMINI_MODEL,
        generation_config={"response_mime_type": "application/json"},
    )

    prompt = f"""
You are an API that extracts structured data from text.

Given a transcription of a patient introducing themselves, return ONLY valid JSON (no prose).

Extract these fields:
- first_name
- last_name
- phone_number (digits only)
- address (string, full sentence)

If any field is missing or uncertain, leave it as null.

Input text:
\"\"\"{transcribed_text.strip()}\"\"\"

Return JSON in this exact format:
{{
  "first_name": "string or null",
  "last_name": "string or null",
  "phone_number": "string or null",
  "address": "string or null"
}}
"""

    resp = model.generate_content(prompt)
    text_out = getattr(resp, "text", "").strip()
    if not text_out:
        raise RuntimeError("Empty response from Gemini")

    try:
        return json.loads(text_out)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid JSON from Gemini: {e}")