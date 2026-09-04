#!/usr/bin/env python3
"""Dependency-light publication and frozen-result validation."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
from pathlib import Path
from typing import Any

try:
    from scoring.aggregate import aggregate
except ModuleNotFoundError:  # Support direct `python scoring/validate.py`.
    from aggregate import aggregate


ROOT = Path(__file__).resolve().parents[1]
CORPUS_ROOT = ROOT / "corpus" / "public-regression" / "0.1.0"
RESULT_ROOT = ROOT / "results" / "v0.1"
BASE_DIMENSIONS = (
    "semantic_correctness",
    "authority_correctness",
    "boundary_correctness",
    "false_positive_discipline",
)
PRIVATE_PATTERNS = {
    "home_path": re.compile(r"/(?:home|Users)/[^/\s]+/"),
    "private_product": re.compile(
        r"(?i)\b(?:" + "Say" + "Hi|Spark" + "Ops|Spark" + "Pyro" + r")\b"
    ),
    "loopback_or_private_ipv4": re.compile(r"\b(?:127\.0\.0\.1|10\.\d+\.\d+\.\d+|192\.168\.\d+\.\d+)\b"),
    "credential_literal": re.compile(r"(?i)(?:ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----|Authorization:\s*Bearer\s+\S+)"),
    "credential_assignment": re.compile(
        r"(?im)^\s*(?:password|passwd|api[_-]?key|access[_-]?token|secret[_-]?key)\s*[:=]\s*[\"']?(?!NOT_(?:RECORDED|PUBLISHED)|UNKNOWN)[^\s\"']{8,}"
    ),
    "cookie_header": re.compile(r"(?i)^\s*(?:cookie|set-cookie):\s*\S+", re.MULTILINE),
}
FORBIDDEN_PUBLIC_NAMES = {
    "raw-response.txt",
    "codex-final.json",
    "codex-events.jsonl",
    "mapping.private.json",
    "response.json",
}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical_sha(value: Any) -> str:
    return sha256_bytes(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    )


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def normalize_aggregate(record: dict[str, Any]) -> dict[str, Any]:
    return json.loads(json.dumps(record, sort_keys=True))


def validate() -> dict[str, Any]:
    errors: list[str] = []
    json_files = sorted(path for path in ROOT.rglob("*.json") if ".git" not in path.parts)
    for path in json_files:
        try:
            load(path)
        except Exception as exc:  # pragma: no cover - diagnostic path
            errors.append(f"JSON parse failed for {path.relative_to(ROOT)}: {exc}")

    corpus_files = [
        CORPUS_ROOT / "upstream.json",
        CORPUS_ROOT / "development-regression.json",
        CORPUS_ROOT / "contrastive.json",
    ]
    cases = []
    subgroup_counts = {}
    for path in corpus_files:
        document = load(path)
        subgroup_counts[document["subgroup"]] = len(document["scenarios"])
        require(document["corpus_role"] == "PUBLIC_REGRESSION_V0", f"wrong corpus role in {path.name}", errors)
        require(document["scenario_count"] == len(document["scenarios"]), f"scenario_count mismatch in {path.name}", errors)
        cases.extend(document["scenarios"])
    ids = [case["metadata"]["case_id"] for case in cases]
    require(len(cases) == 23, "expected exactly 23 public cases", errors)
    require(len(ids) == len(set(ids)), "case IDs are not unique", errors)
    require(subgroup_counts == {
        "CONTRASTIVE": 12,
        "DEVELOPMENT_REGRESSION": 3,
        "UPSTREAM_SPECIFICATION_BOUNDED_DERIVED": 8,
    }, "corpus subgroup counts mismatch", errors)

    strengths: dict[str, int] = {}
    origins: dict[str, int] = {}
    for case in cases:
        meta = case["metadata"]
        strengths[meta["ground_truth_strength"]] = strengths.get(meta["ground_truth_strength"], 0) + 1
        origins[meta["origin_class"]] = origins.get(meta["origin_class"], 0) + 1
        fixture = sha256_bytes(case["prompt_visible"]["prompt"].encode("utf-8"))
        require(fixture == meta["fixture_sha256"], f"fixture digest mismatch: {meta['case_id']}", errors)
        value = copy.deepcopy(case)
        recorded_case_sha = value["metadata"].pop("case_sha256")
        require(canonical_sha(value) == recorded_case_sha, f"case digest mismatch: {meta['case_id']}", errors)
        require(set(case["prompt_visible"]) == {"prompt"}, f"prompt-visible leakage: {meta['case_id']}", errors)
        require(meta["corpus_role"] == "PUBLIC_REGRESSION_V0", f"non-public role: {meta['case_id']}", errors)
    require(strengths == {"AUTHORITATIVE": 6, "DERIVED": 17}, "ground-truth strength counts mismatch", errors)
    require(origins.get("PRIVATE_DERIVED") == 3, "three PRIVATE_DERIVED origins required", errors)

    source_document = load(ROOT / "provenance" / "sources.json")
    sources = {item["source_id"]: item for item in source_document["sources"]}
    require(len(sources) == len(source_document["sources"]), "duplicate source IDs", errors)
    require(all(item["source_sha256"] != "COMPUTED_AT_RELEASE_VALIDATION" for item in sources.values()), "unresolved source digest placeholder", errors)
    for source_id, record in sources.items():
        if record["copied_into_repository"]:
            path = ROOT / record["exact_path"]
            require(path.is_file(), f"internal provenance path missing: {source_id}", errors)
            if path.is_file():
                require(sha256_bytes(path.read_bytes()) == record["source_sha256"], f"internal provenance digest mismatch: {source_id}", errors)
    provenance = load(ROOT / "provenance" / "cases.json")
    provenance_by_id = {item["case_id"]: item for item in provenance["cases"]}
    require(len(provenance_by_id) == 23, "expected provenance for 23 cases", errors)
    require(set(provenance_by_id) == set(ids), "case/provenance ID mismatch", errors)
    for case in cases:
        meta = case["metadata"]
        record = provenance_by_id[meta["case_id"]]
        require(record["fixture_sha256"] == meta["fixture_sha256"], f"provenance fixture mismatch: {meta['case_id']}", errors)
        require(record["case_sha256"] == meta["case_sha256"], f"provenance case mismatch: {meta['case_id']}", errors)
        for source_id in record["source_ids"]:
            require(source_id in sources, f"unresolved provenance source {source_id}: {meta['case_id']}", errors)

    pairs = load(CORPUS_ROOT / "pair-integrity.json")
    require(pairs["pair_count"] == len(pairs["pairs"]) == 6, "expected six pairs", errors)
    paired_ids = []
    for pair in pairs["pairs"]:
        require(len(pair["case_ids"]) == 2, f"pair must have two cases: {pair['pair_id']}", errors)
        paired_ids.extend(pair["case_ids"])
        require(all(case_id in ids for case_id in pair["case_ids"]), f"unresolved pair reference: {pair['pair_id']}", errors)
        require(pair["prompt_leaks_pair_role"] is False, f"pair leakage flag: {pair['pair_id']}", errors)
    contrastive_ids = {
        case["metadata"]["case_id"]
        for case in cases
        if case["metadata"]["subgroup"] == "CONTRASTIVE"
    }
    require(set(paired_ids) == contrastive_ids, "pair membership does not cover contrastive cases exactly", errors)
    role = load(CORPUS_ROOT / "role-history.json")
    require(role["current_role"] == "PUBLIC_REGRESSION_V0", "role history is not public regression", errors)
    require(role["status_at_execution"] == "unseen and locked before the tested skill edit", "historical unseen wording mismatch", errors)
    require(not (ROOT / "corpus" / "unreleased").exists(), "public repository contains an unreleased corpus path", errors)

    grades = load(RESULT_ROOT / "grades.numeric.json")
    hashes = load(RESULT_ROOT / "response-hashes.json")
    require(grades["response_count"] == len(grades["responses"]) == 360, "grade response count mismatch", errors)
    require(grades["grade_count"] == 720, "grade count mismatch", errors)
    require(hashes["response_count"] == len(hashes["responses"]) == 360, "response hash count mismatch", errors)
    grade_ids = {row["sample_id"] for row in grades["responses"]}
    hash_ids = {row["sample_id"] for row in hashes["responses"]}
    require(len(grade_ids) == 360 and grade_ids == hash_ids, "sample/hash ID mismatch", errors)
    require(len({row["raw_response_sha256"] for row in hashes["responses"]}) == 360, "response hashes are not unique", errors)

    scores = load(RESULT_ROOT / "scores.json")
    recomputed = aggregate(RESULT_ROOT / "grades.numeric.json", CORPUS_ROOT)
    expected_aggregates = sorted(
        [normalize_aggregate(item) for item in scores["condition_aggregates"]],
        key=lambda item: (item["corpus"], item["provider"], item["condition"]),
    )
    actual_aggregates = sorted(
        [normalize_aggregate(item) for item in recomputed["condition_aggregates"]],
        key=lambda item: (item["corpus"], item["provider"], item["condition"]),
    )
    require(actual_aggregates == expected_aggregates, "sanitized grades do not reconstruct frozen condition aggregates", errors)
    require(recomputed["inter_rater"] == scores["inter_rater"], "inter-rater statistics mismatch", errors)

    primary = {
        (item["provider"], item["condition"]): item
        for item in scores["condition_aggregates"] if item["corpus"] == "holdout"
    }
    headline = {
        ("qwen", "no-skill"): 5.333,
        ("qwen", "generic-security"): 7.069,
        ("qwen", "spiffe-spire-base"): 5.569,
        ("qwen", "base-plus-adjudicated-revised"): 7.5,
        ("codex", "no-skill"): 7.597,
        ("codex", "generic-security"): 7.847,
        ("codex", "spiffe-spire-base"): 7.236,
        ("codex", "base-plus-adjudicated-revised"): 7.972,
    }
    require(all(primary[key]["mean_base_total"] == value for key, value in headline.items()), "headline values mismatch", errors)
    disagreement = primary[("qwen", "spiffe-spire-base")]["benign_false_positive_rate"]
    require(disagreement["qwen_judge_rate"] == 0.0 and disagreement["codex_judge_rate"] == 1.0 and disagreement["mean_judge_rate"] == 0.5, "base benign-FP disagreement mismatch", errors)
    revised_disagreement = primary[("qwen", "base-plus-adjudicated-revised")]["benign_false_positive_rate"]
    require(revised_disagreement["qwen_judge_rate"] == 0.0 and revised_disagreement["codex_judge_rate"] == 0.1333 and revised_disagreement["mean_judge_rate"] == 0.0667, "revised benign-FP disagreement mismatch", errors)
    require(scores["inter_rater"] == {"dimension_comparisons": 1800, "exact_agreement_rate": 0.8244, "mean_absolute_difference": 0.1878}, "published inter-rater values mismatch", errors)

    manifest = load(RESULT_ROOT / "run-manifest.json")
    require(manifest["raw_response_policy"] == "PUBLISH_HASHES_AND_SCORES_ONLY", "raw-response policy mismatch", errors)
    require(manifest["generic_security_control"]["control_text_publication"] == "DIGEST_AND_METADATA_ONLY", "generic-control disposition mismatch", errors)
    require(manifest["generic_security_control"]["license"] == "NOT_RECORDED", "generic-control license must remain NOT_RECORDED", errors)

    prompts = load(ROOT / "prompts" / "prompts.json")
    for name in ("target_system_prompt", "grader_system_prompt"):
        value = prompts[name]
        encoded = value["text"].encode("utf-8")
        require(len(encoded) == value["bytes"], f"prompt byte mismatch: {name}", errors)
        require(sha256_bytes(encoded) == value["sha256"], f"prompt digest mismatch: {name}", errors)

    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts:
            continue
        require(path.name not in FORBIDDEN_PUBLIC_NAMES, f"forbidden raw/private artifact: {path.relative_to(ROOT)}", errors)
        text = path.read_text(encoding="utf-8", errors="ignore")
        for name, pattern in PRIVATE_PATTERNS.items():
            require(pattern.search(text) is None, f"{name} pattern in {path.relative_to(ROOT)}", errors)
    for path in RESULT_ROOT.glob("*.json"):
        text = path.read_text(encoding="utf-8")
        require('"rationale"' not in text, f"raw grader rationale in {path.name}", errors)
        require('"response": {' not in text, f"raw target response in {path.name}", errors)

    release_manifest = ROOT / "release-manifest.json"
    if release_manifest.is_file():
        frozen = load(release_manifest)
        for record in frozen["files"]:
            path = ROOT / record["path"]
            require(path.is_file(), f"release file missing: {record['path']}", errors)
            if path.is_file():
                require(sha256_bytes(path.read_bytes()) == record["sha256"], f"release file changed: {record['path']}", errors)

    return {
        "case_count": len(cases),
        "errors": errors,
        "grader_calls": 60,
        "matched_pair_count": len(pairs["pairs"]),
        "origin_counts": origins,
        "provenance_case_count": len(provenance_by_id),
        "public_unreleased_holdout_content": False,
        "raw_response_policy": "PUBLISH_HASHES_AND_SCORES_ONLY",
        "response_hash_count": len(hash_ids),
        "response_level_grades": grades["grade_count"],
        "schema": "spiffe-spire-agent-evals-publication-validation/v1",
        "status": "passed" if not errors else "failed",
        "strength_counts": strengths,
        "subgroup_counts": subgroup_counts,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result = validate()
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.write:
        (RESULT_ROOT / "validation.json").write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
