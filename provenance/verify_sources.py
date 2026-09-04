#!/usr/bin/env python3
"""Verify immutable external provenance blobs by SHA-256."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def raw_url(blob_url: str) -> str:
    prefix = "https://github.com/"
    if not blob_url.startswith(prefix) or "/blob/" not in blob_url:
        raise ValueError(f"not an immutable GitHub blob URL: {blob_url}")
    return "https://raw.githubusercontent.com/" + blob_url[len(prefix):].replace("/blob/", "/", 1)


def main() -> int:
    records = json.loads((ROOT / "provenance" / "sources.json").read_text(encoding="utf-8"))["sources"]
    checked = 0
    for record in records:
        if record["content_relationship"] != "PROVENANCE_ONLY":
            continue
        response = subprocess.run(
            [
                "curl",
                "--fail",
                "--location",
                "--silent",
                "--show-error",
                "--retry",
                "3",
                "--connect-timeout",
                "20",
                raw_url(record["canonical_url"]),
            ],
            check=True,
            capture_output=True,
        )
        digest = hashlib.sha256(response.stdout).hexdigest()
        if digest != record["source_sha256"]:
            raise SystemExit(f"digest mismatch: {record['source_id']}")
        checked += 1
    print(f"verified {checked} immutable external source blobs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
