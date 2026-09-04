"""Adapter for a caller-supplied local command using JSON over stdio."""

from __future__ import annotations

import json
import shlex
import subprocess

from runner.protocol import AdapterResult, PreparedRequest


class CommandAdapter:
    def __init__(self, command: str, timeout_seconds: int) -> None:
        self._argv = shlex.split(command)
        if not self._argv:
            raise ValueError("adapter command must not be empty")
        self._timeout = timeout_seconds

    def invoke(self, request: PreparedRequest) -> AdapterResult:
        try:
            completed = subprocess.run(
                self._argv,
                input=json.dumps(request.to_dict(), sort_keys=True).encode("utf-8"),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=self._timeout,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return AdapterResult(status="error", error_category="timeout", error_message="adapter timed out")
        except OSError as exc:
            return AdapterResult(status="error", error_category="transport", error_message=str(exc))
        if completed.returncode != 0:
            return AdapterResult(
                status="error",
                error_category="adapter_exit",
                error_message=f"adapter exited {completed.returncode}",
            )
        return AdapterResult(status="ok", response_bytes=completed.stdout)
