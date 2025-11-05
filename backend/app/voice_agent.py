"""Utilities for communicating with the ElevenLabs speech-to-text API."""
from __future__ import annotations

import io
import logging
import os
import time
from typing import Any, Callable, TypeVar

import certifi
import requests
from fastapi import UploadFile
from dotenv import load_dotenv

from .exceptions import ProviderError

load_dotenv()

logger = logging.getLogger(__name__)

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_STT_URL = "https://api.elevenlabs.io/v1/speech-to-text"

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
            log_kwargs: dict[str, Any] = {
                "event": "voice_agent.retry",
                "operation": operation,
                "attempt": attempt,
                "max_attempts": max_attempts,
            }
            if isinstance(exc, ProviderError):
                log_kwargs.update(exc.to_log_fields())
            else:
                log_kwargs["exception"] = repr(exc)
            log_method = logger.warning if attempt < max_attempts else logger.error
            log_method("Retryable error when calling ElevenLabs", extra=log_kwargs)
            if attempt < max_attempts:
                time.sleep(wait)
    assert last_exc is not None
    raise last_exc


def _safe_payload(resp: requests.Response) -> Any:  # pragma: no cover - best effort
    try:
        return resp.json()
    except ValueError:
        return resp.text[:1000]


def transcribe_audio_data(file: UploadFile) -> str:
    """Send uploaded audio file to ElevenLabs STT and return transcribed text."""
    if not ELEVENLABS_API_KEY:
        raise ValueError("Missing ELEVENLABS_API_KEY")

    if hasattr(file.file, "seek"):
        try:
            file.file.seek(0)
        except Exception:  # pragma: no cover - defensive
            pass

    audio_bytes = file.file.read()
    if not audio_bytes:
        raise RuntimeError("Empty audio file received from frontend")

    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Accept": "application/json",
    }

    def _do_request() -> str:
        files = {
            "file": (file.filename or "recording.webm", io.BytesIO(audio_bytes), file.content_type or "audio/webm"),
        }
        data = {"model_id": "scribe_v1"}

        try:
            resp = requests.post(
                ELEVENLABS_STT_URL,
                headers=headers,
                files=files,
                data=data,
                timeout=90,
                verify=certifi.where(),
            )
        except requests.exceptions.RequestException as exc:
            payload = getattr(exc.response, "text", None)
            raise ProviderError(
                provider="elevenlabs",
                message="Network failure while calling ElevenLabs STT",
                payload=payload[:1000] if isinstance(payload, str) else payload,
            ) from exc

        if resp.status_code >= 400:
            payload = _safe_payload(resp)
            raise ProviderError(
                provider="elevenlabs",
                message="ElevenLabs STT returned an error response",
                status_code=resp.status_code,
                payload=payload,
            )

        result = resp.json()
        text = (result.get("text") or "").strip()
        if not text:
            raise ProviderError(
                provider="elevenlabs",
                message="ElevenLabs STT returned an empty transcript",
                status_code=resp.status_code,
                payload=result,
            )
        return text

    transcript = _retry_with_backoff(_do_request, operation="elevenlabs_transcription")
    logger.info(
        "voice_agent.transcription.success",
        extra={
            "event": "voice_agent.transcription.success",
            "provider": "elevenlabs",
            "char_length": len(transcript),
        },
    )
    return transcript
