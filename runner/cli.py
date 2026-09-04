"""Command-line entry point for one public regression sample."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from runner.adapters.command import CommandAdapter
from runner.core import execute_once, prepare_request


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", type=Path, required=True)
    parser.add_argument("--case-id", required=True)
    parser.add_argument("--condition-id", required=True)
    parser.add_argument("--packet", type=Path)
    parser.add_argument("--adapter-command", required=True)
    parser.add_argument("--model-config", type=Path, required=True)
    parser.add_argument("--sample-id", default="sample-0001")
    parser.add_argument("--output", type=Path, default=Path(".runs"))
    parser.add_argument("--timeout-seconds", type=int, default=600)
    parser.add_argument("--prompts", type=Path, default=Path("prompts/prompts.json"))
    args = parser.parse_args()

    prompts = json.loads(args.prompts.read_text(encoding="utf-8"))
    model_config = json.loads(args.model_config.read_text(encoding="utf-8"))
    request = prepare_request(
        corpus_path=args.corpus,
        case_id=args.case_id,
        condition_id=args.condition_id,
        packet_path=args.packet,
        model_config=model_config,
        system_prompt=prompts["target_system_prompt"]["text"],
        sample_id=args.sample_id,
    )
    result_path = execute_once(
        CommandAdapter(args.adapter_command, args.timeout_seconds), request, args.output
    )
    print(result_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
