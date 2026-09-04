#!/usr/bin/env python3
"""Create the immutable-file digest inventory used by release CI."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "release-manifest.json"
EXCLUDED_PARTS = {".git", "__pycache__", ".runs", ".venv"}


def main() -> int:
    files = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or path == OUTPUT:
            continue
        relative = path.relative_to(ROOT)
        if any(part in EXCLUDED_PARTS for part in relative.parts):
            continue
        files.append(
            {
                "path": relative.as_posix(),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
        )
    OUTPUT.write_text(
        json.dumps(
            {
                "corpus_version": "0.1.0",
                "file_count": len(files),
                "files": files,
                "release": "v0.1.0",
                "runner_version": "0.1.0",
                "schema": "spiffe-spire-agent-evals-release-manifest/v1",
                "scorer_version": "0.1.0",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
