"""Shared exception utilities for the voice agent backend."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass
class ProviderError(RuntimeError):
    """Exception raised when an upstream AI/STT provider fails."""

    provider: str
    message: str
    status_code: int | None = None
    payload: Any | None = None

    def __post_init__(self) -> None:  # pragma: no cover - trivial
        super().__init__(self.message)

    def to_log_fields(self) -> Mapping[str, Any]:
        fields = {
            "provider": self.provider,
            "status_code": self.status_code,
        }
        if self.payload is not None:
            fields["payload"] = self.payload
        return fields
