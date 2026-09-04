"""Case selection, prompt construction, and one-attempt execution."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from runner.protocol import Adapter, PreparedRequest


TASK_TEXT = """Assess every distinct concern in the scenario. Use calibrated claim strength, identify the owning
boundary, and state exactly what evidence would be required to make any stronger claim. The scenario
is self-contained: do not seek or claim access to omitted implementation or runtime evidence."""


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def select_prompt_visible(corpus_path: Path, case_id: str) -> dict[str, Any]:
    """Return only prompt-visible data; never return the ground-truth object."""
    corpus = load_json(corpus_path)
    matches = [case for case in corpus["scenarios"] if case["metadata"]["case_id"] == case_id]
    if len(matches) != 1:
        raise ValueError(f"expected exactly one case {case_id!r}, found {len(matches)}")
    case = matches[0]
    prompt = case["prompt_visible"]
    if set(prompt) != {"prompt"}:
        raise ValueError("prompt_visible contains an unexpected field")
    digest = sha256_bytes(prompt["prompt"].encode("utf-8"))
    if digest != case["metadata"]["fixture_sha256"]:
        raise ValueError("fixture digest mismatch")
    return {
        "case_id": case_id,
        "fixture_sha256": digest,
        "prompt": prompt["prompt"],
    }


def build_user_prompt(case_prompt: str, packet: str | None) -> str:
    packet_text = packet if packet is not None else "(No additional security-review reference packet supplied.)"
    return (
        "SECURITY-REVIEW SCENARIO\n\n"
        + case_prompt
        + "\n\nREFERENCE PACKET\n\n"
        + packet_text
        + "\n\nTASK\n\n"
        + TASK_TEXT
    )


def prepare_request(
    *,
    corpus_path: Path,
    case_id: str,
    condition_id: str,
    packet_path: Path | None,
    model_config: dict[str, Any],
    system_prompt: str,
    sample_id: str,
) -> PreparedRequest:
    selected = select_prompt_visible(corpus_path, case_id)
    packet = packet_path.read_text(encoding="utf-8") if packet_path else None
    user_prompt = build_user_prompt(selected["prompt"], packet)
    request_digest = sha256_bytes((system_prompt + "\n\n" + user_prompt).encode("utf-8"))
    return PreparedRequest(
        sample_id=sample_id,
        case_id=case_id,
        condition_id=condition_id,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        fixture_sha256=selected["fixture_sha256"],
        request_sha256=request_digest,
        model_config=model_config,
    )


def execute_once(adapter: Adapter, request: PreparedRequest, output_root: Path) -> Path:
    """Execute exactly once and persist success separately from failure."""
    sample_dir = output_root / request.sample_id
    sample_dir.mkdir(parents=True, exist_ok=False)
    (sample_dir / "request.public.json").write_text(
        json.dumps(request.to_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    result = adapter.invoke(request)
    if result.status != "ok":
        path = sample_dir / "error.json"
        path.write_text(
            json.dumps(
                {
                    "status": "error",
                    "error_category": result.error_category,
                    "error_message": result.error_message,
                    "retry_count": 0,
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        return path
    response_hash = sha256_bytes(result.response_bytes)
    raw_path = sample_dir / "response.json"
    raw_path.write_bytes(result.response_bytes)
    path = sample_dir / "result.public.json"
    path.write_text(
        json.dumps(
            {
                "status": "ok",
                "sample_id": request.sample_id,
                "case_id": request.case_id,
                "condition_id": request.condition_id,
                "fixture_sha256": request.fixture_sha256,
                "request_sha256": request.request_sha256,
                "response_sha256": response_hash,
                "response_path": str(raw_path.relative_to(output_root)),
                "retry_count": 0,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return path
