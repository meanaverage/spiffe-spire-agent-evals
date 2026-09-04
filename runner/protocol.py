"""Provider-neutral adapter protocol."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class PreparedRequest:
    sample_id: str
    case_id: str
    condition_id: str
    system_prompt: str
    user_prompt: str
    fixture_sha256: str
    request_sha256: str
    model_config: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AdapterResult:
    status: str
    response_bytes: bytes = b""
    error_category: str | None = None
    error_message: str | None = None


class Adapter(Protocol):
    def invoke(self, request: PreparedRequest) -> AdapterResult:
        """Perform one attempt. Adapters must not silently retry."""
