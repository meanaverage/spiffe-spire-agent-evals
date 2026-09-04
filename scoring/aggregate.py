#!/usr/bin/env python3
"""Reconstruct condition aggregates from sanitized per-response grades."""

from __future__ import annotations

import argparse
import json
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any


BASE_DIMENSIONS = (
    "semantic_correctness",
    "authority_correctness",
    "boundary_correctness",
    "false_positive_discipline",
)
ALL_DIMENSIONS = BASE_DIMENSIONS + ("claim_label_consistency",)
FLAGS = ("overclaim", "underclaim", "contradictory_label")


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def rate(values: list[bool]) -> float:
    return round(sum(values) / len(values), 4) if values else 0.0


def flag_rates(rows: list[dict[str, Any]], flag: str) -> dict[str, float]:
    qwen = [row["grader_scores"]["qwen"][flag] for row in rows]
    codex = [row["grader_scores"]["codex"][flag] for row in rows]
    return {
        "both_graders_rate": rate([a and b for a, b in zip(qwen, codex)]),
        "codex_judge_rate": rate(codex),
        "either_grader_rate": rate([a or b for a, b in zip(qwen, codex)]),
        "mean_judge_rate": round((sum(qwen) + sum(codex)) / (2 * len(rows)), 4),
        "qwen_judge_rate": rate(qwen),
    }


def expected_classifications(corpus_root: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for path in sorted(corpus_root.glob("*.json")):
        document = load(path)
        for case in document.get("scenarios", []):
            classes = case["metadata"]["expected_claim_classes"]
            if classes and classes[0] != "NOT_RECORDED":
                values[case["metadata"]["case_id"]] = classes[0]
    return values


def aggregate(grades_path: Path, corpus_root: Path) -> dict[str, Any]:
    grades = load(grades_path)["responses"]
    expected = expected_classifications(corpus_root)
    groups: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in grades:
        frozen_corpus = (
            "holdout" if row["corpus_role"] == "PUBLIC_REGRESSION_V0" else "development-regression"
        )
        groups[(frozen_corpus, row["target_configuration_id"], row["condition"])].append(row)

    aggregates = []
    for (corpus, provider, condition), rows in sorted(groups.items()):
        record: dict[str, Any] = {
            "base_total_standard_deviation": round(
                statistics.pstdev(row["mean_base_total"] for row in rows), 3
            ),
            "condition": condition,
            "contradictory_label_rate": flag_rates(rows, "contradictory_label"),
            "corpus": corpus,
            "dimension_means": {
                dimension: round(
                    sum(row["mean_scores"][dimension] for row in rows) / len(rows), 3
                )
                for dimension in ALL_DIMENSIONS
            },
            "mean_base_total": round(
                sum(row["mean_base_total"] for row in rows) / len(rows), 3
            ),
            "overclaim_rate": flag_rates(rows, "overclaim"),
            "provider": provider,
            "samples": len(rows),
            "underclaim_rate": flag_rates(rows, "underclaim"),
        }
        if corpus == "holdout":
            benign = [
                row
                for row in rows
                if expected.get(row["scenario_id"]) == "NON_FINDING"
            ]
            positive = [
                row
                for row in rows
                if expected.get(row["scenario_id"]) not in {None, "NON_FINDING"}
            ]
            record["benign_false_positive_rate"] = flag_rates(benign, "overclaim")
            record["positive_underclaim_rate"] = flag_rates(positive, "underclaim")
        aggregates.append(record)

    comparisons = 0
    exact = 0
    absolute = 0
    for row in grades:
        for dimension in ALL_DIMENSIONS:
            qwen = row["grader_scores"]["qwen"][dimension]
            codex = row["grader_scores"]["codex"][dimension]
            comparisons += 1
            exact += qwen == codex
            absolute += abs(qwen - codex)
    return {
        "condition_aggregates": aggregates,
        "inter_rater": {
            "dimension_comparisons": comparisons,
            "exact_agreement_rate": round(exact / comparisons, 4),
            "mean_absolute_difference": round(absolute / comparisons, 4),
        },
        "schema": "spiffe-spire-agent-evals-recomputed-aggregates/v1",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("grades", type=Path)
    parser.add_argument(
        "--corpus-root",
        type=Path,
        default=Path("corpus/public-regression/0.1.0"),
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = aggregate(args.grades, args.corpus_root)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
