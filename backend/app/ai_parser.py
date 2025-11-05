"""LLM parser helpers for extracting structured patient information."""
from __future__ import annotations

import json
import logging
import os
import textwrap
import time
from typing import Any, Callable, TypeVar

from dotenv import load_dotenv
import google.generativeai as genai

from .exceptions import ProviderError

load_dotenv()

logger = logging.getLogger(__name__)

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("Missing GEMINI_API_KEY in environment")

genai.configure(api_key=GEMINI_API_KEY)

T = TypeVar("T")


def _retry_with_backoff(
    fn: Callable[[], T],
    *,
    operation: str,
    max_attempts: int = 3,
    base_delay: float = 1.0,
) -> T:
    """Retry ``fn`` with exponential backoff."""
    last_exc: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            return fn()
        except Exception as exc:  # pragma: no cover - network heavy
            last_exc = exc
            wait = base_delay * (2 ** (attempt - 1))
            log_fields: dict[str, Any] = {
                "event": "ai_parser.retry",
                "operation": operation,
                "attempt": attempt,
                "max_attempts": max_attempts,
            }
            if isinstance(exc, ProviderError):
                log_fields.update(exc.to_log_fields())
            else:
                log_fields["exception"] = repr(exc)
            log_method = logger.warning if attempt < max_attempts else logger.error
            log_method("Retryable error when calling Gemini", extra=log_fields)
            if attempt < max_attempts:
                time.sleep(wait)
    assert last_exc is not None
    raise last_exc


def _truncate(value: Any, limit: int = 1000) -> Any:  # pragma: no cover - formatting helper
    if isinstance(value, str) and len(value) > limit:
        return value[:limit] + "…"
    return value


def parse_patient_details(transcribed_text: str) -> dict:
    """Extract structured patient data from a speech transcript using Gemini."""
    model = genai.GenerativeModel(
        model_name=GEMINI_MODEL,
        generation_config={"response_mime_type": "application/json"},
    )

    cleaned_transcript = transcribed_text.strip()
    prompt = (
        "You are an API that extracts structured data from text.\n\n"
        "Given a transcription of a patient introducing themselves, return ONLY valid JSON (no prose).\n\n"
        "Extract these fields:\n"
        "- first_name\n"
        "- last_name\n"
        "- phone_number (digits only)\n"
        "- address (string, full sentence)\n\n"
        "If any field is missing or uncertain, leave it as null.\n\n"
        f"Input text:\n\"\"\"{cleaned_transcript}\"\"\"\n\n"
        "Return JSON in this exact format (and nothing else):\n\n"
        "{\n"
        '  "first_name": "string or null",\n'
        '  "last_name": "string or null",\n'
        '  "phone_number": "string or null",\n'
        '  "address": "string or null"\n'
        "}\n"
    )

    def _generate() -> str:
        try:
            resp = model.generate_content(prompt)
        except Exception as exc:
            payload = getattr(getattr(exc, "response", None), "text", None)
            raise ProviderError(
                provider="gemini",
                message="Gemini generate_content call failed",
                payload=_truncate(payload),
            ) from exc

        text_out = getattr(resp, "text", "").strip()
        if not text_out:
            raise ProviderError(
                provider="gemini",
                message="Gemini returned an empty response",
                payload=getattr(resp, "to_dict", lambda: {})(),
            )
        return text_out

    raw_json = _retry_with_backoff(_generate, operation="gemini_generate")
    logger.info(
        "ai_parser.parsing.success",
        extra={
            "event": "ai_parser.parsing.success",
            "provider": "gemini",
            "response_chars": len(raw_json),
        },
    )

    try:
        return json.loads(raw_json)
    except json.JSONDecodeError as exc:
        raise ProviderError(
            provider="gemini",
            message=f"Invalid JSON from Gemini: {exc}",
            payload=_truncate(raw_json),
        ) from exc
