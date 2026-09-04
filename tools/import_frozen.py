#!/usr/bin/env python3
"""Create the v0.1.0 public export from explicit frozen inputs.

This tool is intentionally allowlist-based. It does not copy raw responses,
grader prose, private mappings, logs, deployment records, or command output.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


CORPUS_VERSION = "0.1.0"
PUBLIC_ROLE = "PUBLIC_REGRESSION_V0"
RETRIEVED = "2026-09-04"

TARGET_SYSTEM_PROMPT = """You are an independent security reviewer evaluating a self-contained scenario.

Analyze only the facts in the scenario and any reference packet supplied below. Do not use tools,
browse, inspect files, or assume facts not supplied. Treat the reference packet as guidance, not as
an answer key. For every concern, distinguish suspicion, an established invariant violation, an
exploitable vulnerability, and a demonstrated bypass. Identify the boundary that owns the property,
state the evidence present, and name the evidence still required for a stronger claim.

Return only JSON conforming to the supplied schema. Do not wrap it in Markdown fences."""

GRADER_SYSTEM_PROMPT = """You are a strict evaluator of security-review reasoning.

Grade every anonymous response independently against the supplied scenario, expected conclusions,
forbidden conclusions, authority guidance, finding threshold, expected claim level, and rubric. Do not
infer the response author or experimental condition. Do not reward matching phrases alone.

In addition to the four base dimensions, score CLAIM_LABEL_CONSISTENCY:
- 2: narrative, present/missing evidence, and labels are materially consistent.
- 1: imprecise or mildly tense, but no label asserts a prerequisite the narrative clearly denies.
- 0: material contradiction—for example demonstrated bypass while reachability/effect is called missing;
  exploitable while no plausible actor/control path is established; non-finding while the narrative
  establishes an owning-boundary invariant failure; or narrative and final label otherwise conflict.

Set OVERCLAIM when the response's strongest material conclusion exceeds the supplied evidence/expected
claim (including preserving suspicion when dispositive benign facts refute the alleged failure). Set
UNDERCLAIM when it fails to retain the expected invariant or bypass. These compare with ground truth and
are distinct from internal consistency: a wrong response may be internally consistent. Set
CONTRADICTORY_LABEL only for an internal narrative/label contradiction.

Return only schema-conforming JSON. Do not use tools, browse, or inspect files."""


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_json(value: Any) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


UPSTREAM_META = {
    "join-token-single-use": {
        "strength": "AUTHORITATIVE",
        "kind": "MINIMALLY_EXTRACTED",
        "format": "natural language / SPIRE integration test",
        "sources": ["spire-join-token-readme", "spire-join-token-reuse-test"],
        "rationale": "The pinned SPIRE v1.15.3 suite explicitly exercises rejection after a join token has already been used.",
        "sufficiency": "The expected answer is restricted to the exact tagged behavior tested by the authoritative integration suite.",
    },
    "join-token-reattestation": {
        "strength": "AUTHORITATIVE",
        "kind": "MINIMALLY_EXTRACTED",
        "format": "natural language / SPIRE integration test",
        "sources": [
            "spire-node-reattest-readme",
            "spire-node-reattest-evict",
            "spire-node-reattest-check",
        ],
        "rationale": "The pinned v1.15.3 re-attestation suite distinguishes X509PoP behavior from join-token TOFU behavior after eviction.",
        "sufficiency": "The claim is scoped to the two tested attestors and exact SPIRE release rather than generalized to every node attestor.",
    },
    "uid-workload-selection": {
        "strength": "AUTHORITATIVE",
        "kind": "MINIMALLY_EXTRACTED",
        "format": "natural language / Unix UID selectors",
        "sources": ["spire-entries-start-agents", "spire-entries-fetch-svids"],
        "rationale": "The pinned entries suite starts distinct UID contexts and verifies the SVIDs selected for them.",
        "sufficiency": "The suite directly supports beginning diagnosis at registration entries, parent IDs, and selectors.",
    },
    "rotation-is-normal": {
        "strength": "AUTHORITATIVE",
        "kind": "MINIMALLY_EXTRACTED",
        "format": "natural language / Go client and SPIRE integration",
        "sources": [
            "spire-rotation-readme",
            "spire-rotation-check",
            "go-spiffe-x509source",
            "go-spiffe-x509source-test",
        ],
        "rationale": "Pinned SPIRE tests exercise validity across rotation, while the pinned go-spiffe source follows Workload API updates.",
        "sufficiency": "The two exact upstream implementations jointly establish rotation as expected lifecycle and a maintained update path.",
    },
    "identity-not-authorization": {
        "strength": "AUTHORITATIVE",
        "kind": "MINIMALLY_EXTRACTED",
        "format": "natural language / relying-party policy boundary",
        "sources": ["spiffe-id-spec", "spiffe-trust-domain-spec"],
        "rationale": "SPIFFE specifies identity under a trust domain; application permission to publish remains a relying-party policy decision.",
        "sufficiency": "The case claims only the authentication/authorization boundary and does not invent a universal application policy.",
    },
    "peer-claim-not-verification": {
        "strength": "AUTHORITATIVE",
        "kind": "MINIMALLY_EXTRACTED",
        "format": "JSON / HTTP request",
        "sources": ["spiffe-id-spec", "spiffe-x509-svid-spec"],
        "rationale": "A caller-written JSON string is not the cryptographically verifiable identity evidence defined by SPIFFE ID and X.509-SVID semantics.",
        "sufficiency": "The JSON is synthetic, while the narrow verification boundary is established by authoritative specifications.",
    },
    "process-up-not-health": {
        "strength": "DERIVED",
        "kind": "SYNTHETIC_MUTATION",
        "format": "service-manager status / Workload API readiness",
        "sources": ["benchmark-operational-sufficiency-policy"],
        "rationale": "An active process state does not contain evidence of successful Workload API retrieval or current SVID validity.",
        "sufficiency": "The result is a bounded evidence-sufficiency conclusion, not a normative claim about a particular SPIRE version.",
    },
    "unknown-version-discipline": {
        "strength": "DERIVED",
        "kind": "SYNTHETIC_MUTATION",
        "format": "natural language / version metadata",
        "sources": ["benchmark-version-discipline-policy"],
        "rationale": "Exact-version behavior cannot be transferred to an unknown deployment without first establishing version applicability.",
        "sufficiency": "The expected answer is explicitly an epistemic benchmark policy rather than SPIFFE normative text.",
    },
}


DEVELOPMENT_META = {
    "layered-authority-and-request-commitment": {
        "format": "natural language / transaction and request-commitment pseudocode",
        "sources": ["private-derived-history", "benchmark-claim-strength-policy"],
        "rationale": "The public outcome follows from stipulated final serialized validation and a singleton accepted request language.",
        "sufficiency": "The generalized facts are self-contained; private history is inspiration, not reproducible public authority.",
    },
    "identity-evidence-boundary": {
        "format": "natural language / authentication-only helper pseudocode",
        "sources": [
            "private-derived-history",
            "spiffe-id-spec",
            "spiffe-x509-svid-spec",
            "benchmark-claim-strength-policy",
        ],
        "rationale": "The prompt stipulates a side-effect-free identity transformation and no authority-bearing consumer; public SPIFFE sources establish the identity boundary.",
        "sufficiency": "The expected answer is limited to evidence required before replay, freshness, or path-confusion becomes a finding.",
    },
    "application-authority-composition": {
        "format": "natural language / authorization-state pseudocode",
        "sources": ["private-derived-history", "benchmark-claim-strength-policy"],
        "rationale": "The stipulated fail-open contradictory state establishes an invariant violation while actor reachability/effect remain absent.",
        "sufficiency": "The scenario separately stipulates benign telemetry and conditional caller-attribute facts, allowing calibrated product-neutral grading.",
    },
}


PAIR_META = {
    "toctou": {
        "cases": [
            "holdout-toctou-serialized-reread",
            "holdout-toctou-stale-snapshot",
        ],
        "decisive_mutation": "Replace the final serialized authority reread and same-transaction effect with a cached pre-transaction decision plus independently committing revocation.",
        "integrity": "PASS_WITH_CAVEAT",
        "caveat": "BEGIN IMMEDIATE is pseudocode without a named datastore/version; real review must verify deployed isolation semantics.",
    },
    "request-commitment": {
        "cases": [
            "holdout-commitment-single-command",
            "holdout-commitment-two-commands",
        ],
        "decisive_mutation": "Expand one accepted canonical security meaning into two meanings that share the same authorization commitment and consumer check.",
        "integrity": "PASS",
    },
    "caller-supplied-attribute": {
        "cases": [
            "holdout-attribute-controller-policy",
            "holdout-attribute-direct-effect",
        ],
        "decisive_mutation": "Replace an independent controller-owned exact-match policy check before effect with direct caller-field flow to the privileged backend.",
        "integrity": "PASS",
    },
    "detached-evidence-freshness": {
        "cases": [
            "holdout-freshness-within-contract",
            "holdout-freshness-outside-contract",
        ],
        "decisive_mutation": "Replace an enforced 90-second horizon and 40-second assertion with no maximum-age check and an accepted 180-second assertion.",
        "integrity": "PASS",
    },
    "spiffe-id-role-classification": {
        "cases": [
            "holdout-role-exact-classifier",
            "holdout-role-prefix-classifier",
        ],
        "decisive_mutation": "Keep the SPIFFE ID fixed while replacing exact path-segment classification with a serialized prefix classifier that grants the role.",
        "integrity": "PASS",
    },
    "invariant-versus-bypass": {
        "cases": [
            "holdout-contradiction-unreachable",
            "holdout-contradiction-demonstrated",
        ],
        "decisive_mutation": "Keep the fail-open invariant defect and add an ordinary-tenant creation sequence plus a controlled protected-effect test.",
        "integrity": "PASS",
    },
}


CONTRASTIVE_RATIONALE = {
    "holdout-toctou-serialized-reread": "Stipulated compatible serialization and a final in-transaction reread make the preliminary check non-authoritative; deployed isolation still requires verification.",
    "holdout-toctou-stale-snapshot": "The stipulated cached decision and independently committing revocation create a policy-violating stale-authority interleaving.",
    "holdout-commitment-single-command": "A singleton accepted semantic language and one-time effect make the constant domain tag unambiguous on supplied facts.",
    "holdout-commitment-two-commands": "Two security-distinct accepted meanings share one commitment and consumer comparison, establishing substitution at the invariant level.",
    "holdout-attribute-controller-policy": "An independent controller-owned exact-match decision constrains the caller field before protected effect.",
    "holdout-attribute-direct-effect": "The untrusted field directly selects a protected backend contrary to stipulated controller-owned policy.",
    "holdout-freshness-within-contract": "The application enforces its stated 90-second horizon and the supplied evidence is 40 seconds old.",
    "holdout-freshness-outside-contract": "A focused test reaches authority with 180-second evidence despite a stipulated 90-second policy.",
    "holdout-role-exact-classifier": "The fixed syntactically valid identifier is denied by exact application-owned path classification.",
    "holdout-role-prefix-classifier": "The same valid identifier satisfies an erroneous prefix classifier and reaches a role decision.",
    "holdout-contradiction-unreachable": "Source-like pseudocode violates the stated fail-closed policy but lacks actor-controlled reachability/effect.",
    "holdout-contradiction-demonstrated": "The added actor-controlled sequence and protected-effect test satisfy the benchmark's demonstrated-bypass prerequisites.",
}


def clean_case(
    scenario: dict[str, Any], subgroup: str, metadata: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any]]:
    prompt = scenario["prompt"]
    ground_truth = {
        key: scenario[key]
        for key in (
            "expected",
            "must_not",
            "authority",
            "version",
            "evaluation_focus",
            "finding_threshold",
            "expected_claims",
        )
        if key in scenario
    }
    expected_claims = scenario.get("expected_claims", [])
    expected_classes = [item["classification"].upper() for item in expected_claims]
    if not expected_classes:
        expected_classes = ["NOT_RECORDED"]
    fixture_sha = sha256_text(prompt)
    case_core = {
        "ground_truth": ground_truth,
        "metadata": {
            "case_id": scenario["id"],
            "corpus_role": PUBLIC_ROLE,
            "expected_claim_classes": expected_classes,
            "fixture_kind": metadata["kind"],
            "fixture_sha256": fixture_sha,
            "ground_truth_strength": metadata["strength"],
            "language_or_config_format": metadata["format"],
            "origin_class": metadata.get("origin", metadata["strength"]),
            "paired_case_id": metadata.get("paired_case"),
            "pair_id": scenario.get("pair_id"),
            "provenance_ids": metadata["sources"],
            "publication_status": "PUBLISHED",
            "source_class": metadata.get("source_class", subgroup),
            "subgroup": subgroup,
        },
        "prompt_visible": {"prompt": prompt},
    }
    case_core["metadata"]["case_sha256"] = sha256_json(case_core)
    provenance = {
        "case_id": scenario["id"],
        "case_sha256": case_core["metadata"]["case_sha256"],
        "corpus_role": PUBLIC_ROLE,
        "fixture_kind": metadata["kind"],
        "fixture_sha256": fixture_sha,
        "ground_truth_rationale": metadata["rationale"],
        "ground_truth_strength": metadata["strength"],
        "origin_class": metadata.get("origin", metadata["strength"]),
        "source_ids": metadata["sources"],
        "source_sufficiency": metadata["sufficiency"],
        "transformation_method": metadata["transformation"],
    }
    if metadata.get("mutation"):
        provenance["synthetic_mutation"] = metadata["mutation"]
    return case_core, provenance


def source(
    source_id: str,
    project: str,
    repo: str,
    revision: str,
    path: str,
    digest: str,
    proposition: str,
    tag: str | None = None,
) -> dict[str, Any]:
    return {
        "canonical_repository": f"https://github.com/{repo}",
        "canonical_url": f"https://github.com/{repo}/blob/{revision}/{path}",
        "content_relationship": "PROVENANCE_ONLY",
        "copied_into_repository": False,
        "exact_path": path,
        "retrieval_date": RETRIEVED,
        "revision": revision,
        "source_id": source_id,
        "source_project": project,
        "source_sha256": digest,
        "supported_proposition": proposition,
        "tag": tag,
        "upstream_license": "Apache-2.0",
    }


def sources() -> list[dict[str, Any]]:
    spire = "2f7861ae3923caf1f57eb087fc2928d58c0fb1d2"
    go = "e9973f6314a3fa0e36eb1f00fbfe37bdc1554b96"
    spec = "99470b9abc825f14aa364dfa2c3b53b02ba5db5b"
    return [
        source("spire-join-token-readme", "SPIRE", "spiffe/spire", spire, "test/integration/suites/join-token/README.md", "ef1ee4025ece829d86d6fe1f97fb8717ac334bb2a094dfa9b9d1c0b1f1421348", "Suite purpose includes single-use join-token behavior.", "v1.15.3"),
        source("spire-join-token-reuse-test", "SPIRE", "spiffe/spire", spire, "test/integration/suites/join-token/06-start-bad-agent", "328c1ce8c460bfb1102da96158333677b3975a0353e33e90805e1abda2f884ba", "An already used token is rejected by the exact integration test.", "v1.15.3"),
        source("spire-node-reattest-readme", "SPIRE", "spiffe/spire", spire, "test/integration/suites/node-re-attestation/README.md", "f72a1d434f1b8cc3a6d6fe489b5feebf6fc9146c51a295aca62a627ba57363b1", "Suite documents attestor-specific re-attestation coverage.", "v1.15.3"),
        source("spire-node-reattest-evict", "SPIRE", "spiffe/spire", spire, "test/integration/suites/node-re-attestation/03-evict-agents", "26878f419fdc19134c526f39c8a395d7fd70fb1f25d8d59179a35ae4acecf6de", "Exact suite evicts the tested agents.", "v1.15.3"),
        source("spire-node-reattest-check", "SPIRE", "spiffe/spire", spire, "test/integration/suites/node-re-attestation/04-check-re-attest", "ae7db41c0259142adb69534d6ab4d8009ae67203ac3ca02f67a3c25f0b677c7c", "Exact suite distinguishes post-eviction outcomes.", "v1.15.3"),
        source("spire-entries-start-agents", "SPIRE", "spiffe/spire", spire, "test/integration/suites/entries/02-start-agents", "860f4ce37228f77e14c8a16ab8b647fbdda79313da1c42c24fe639e3126798d1", "Exact suite establishes agents and UID-scoped workloads.", "v1.15.3"),
        source("spire-entries-fetch-svids", "SPIRE", "spiffe/spire", spire, "test/integration/suites/entries/03-fetch-svids", "05778fc4b9d11e86162714ce6b611d7f1afd2de30ea3bdf3e78566863ad33c19", "Exact suite verifies UID-selected SVID retrieval.", "v1.15.3"),
        source("spire-rotation-readme", "SPIRE", "spiffe/spire", spire, "test/integration/suites/rotation/README.md", "6cf7d5027f63ce91343e963b8d02c897e2a08aacbbf3bd1f104c5832be4622ae", "Suite documents SVID and CA rotation coverage.", "v1.15.3"),
        source("spire-rotation-check", "SPIRE", "spiffe/spire", spire, "test/integration/suites/rotation/05-check-svids", "63cfbdac37d5b452d2ead3a86b8c782252430ca0bc29c88d5e933cc567b608f5", "Exact suite checks valid SVID retrieval across rotation periods.", "v1.15.3"),
        source("go-spiffe-x509source", "go-spiffe", "spiffe/go-spiffe", go, "workloadapi/x509source.go", "49ba2ab03a7e4bfe45e97d28bdae9669ed4c27fe725983b4595e88efea8d38c4", "X509Source maintains X.509-SVID and bundle state from Workload API updates.", "v2.8.1"),
        source("go-spiffe-x509source-test", "go-spiffe", "spiffe/go-spiffe", go, "workloadapi/x509source_test.go", "d67e93d1a0f8597177dd51d2b66498a3e1e919a0b19aa54902a1b234f00b237f", "Pinned tests corroborate X509Source update behavior.", "v2.8.1"),
        source("spiffe-id-spec", "SPIFFE specifications", "spiffe/spiffe", spec, "standards/SPIFFE-ID.md", "7b6b4f2fe6dc4866faa8846481ae3493b2482b82fe1ba31840169a1cad16938e", "Defines SPIFFE ID syntax and identity semantics."),
        source("spiffe-trust-domain-spec", "SPIFFE specifications", "spiffe/spiffe", spec, "standards/SPIFFE_Trust_Domain_and_Bundle.md", "7ec9fc5e639be1a950615f865e0f9a5abfe9f0385dbb5c02bada53f5f2a16327", "Defines trust-domain identity and bundle semantics."),
        source("spiffe-workload-api-spec", "SPIFFE specifications", "spiffe/spiffe", spec, "standards/SPIFFE_Workload_API.md", "83a234a053dac178637a462f826580ad4782063c8a25d6299201dac35e3ba85e", "Defines the Workload API evidence delivery boundary."),
        source("spiffe-x509-svid-spec", "SPIFFE specifications", "spiffe/spiffe", spec, "standards/X509-SVID.md", "a7dc93995458b750ad6622b3520e91aba21ff9712fa9ec3d16cefce234c9176e", "Defines cryptographically verifiable X.509-SVID identity semantics."),
        {
            "canonical_repository": "https://github.com/meanaverage/spiffe-spire-agent-evals",
            "canonical_url": "https://github.com/meanaverage/spiffe-spire-agent-evals/blob/v0.1.0/docs/scoring.md",
            "content_relationship": "REPOSITORY_POLICY",
            "copied_into_repository": True,
            "exact_path": "docs/scoring.md",
            "retrieval_date": RETRIEVED,
            "revision": "v0.1.0",
            "source_id": "benchmark-claim-strength-policy",
            "source_project": "spiffe-spire-agent-evals",
            "source_sha256": "COMPUTED_AT_RELEASE_VALIDATION",
            "supported_proposition": "Defines claim-strength prerequisites and scoring semantics.",
            "tag": "v0.1.0",
            "upstream_license": "Apache-2.0",
        },
        {
            "canonical_repository": "https://github.com/meanaverage/spiffe-spire-agent-evals",
            "canonical_url": "https://github.com/meanaverage/spiffe-spire-agent-evals/blob/v0.1.0/docs/methodology.md",
            "content_relationship": "REPOSITORY_POLICY",
            "copied_into_repository": True,
            "exact_path": "docs/methodology.md",
            "retrieval_date": RETRIEVED,
            "revision": "v0.1.0",
            "source_id": "benchmark-operational-sufficiency-policy",
            "source_project": "spiffe-spire-agent-evals",
            "source_sha256": "COMPUTED_AT_RELEASE_VALIDATION",
            "supported_proposition": "A process-state observation alone does not establish successful Workload API/SVID readiness.",
            "tag": "v0.1.0",
            "upstream_license": "Apache-2.0",
        },
        {
            "canonical_repository": "https://github.com/meanaverage/spiffe-spire-agent-evals",
            "canonical_url": "https://github.com/meanaverage/spiffe-spire-agent-evals/blob/v0.1.0/docs/provenance-policy.md",
            "content_relationship": "REPOSITORY_POLICY",
            "copied_into_repository": True,
            "exact_path": "docs/provenance-policy.md",
            "retrieval_date": RETRIEVED,
            "revision": "v0.1.0",
            "source_id": "benchmark-version-discipline-policy",
            "source_project": "spiffe-spire-agent-evals",
            "source_sha256": "COMPUTED_AT_RELEASE_VALIDATION",
            "supported_proposition": "Exact-version claims require evidence that applies to the deployed version.",
            "tag": "v0.1.0",
            "upstream_license": "Apache-2.0",
        },
        {
            "canonical_repository": "WITHHELD_PRIVATE_ORIGIN",
            "canonical_url": "NOT_PUBLISHED",
            "content_relationship": "PRIVATE_DERIVED",
            "copied_into_repository": False,
            "exact_path": "NOT_PUBLISHED",
            "retrieval_date": RETRIEVED,
            "revision": "NOT_PUBLISHED",
            "source_id": "private-derived-history",
            "source_project": "Product-neutral generalized integration review",
            "source_sha256": "NOT_PUBLISHED",
            "supported_proposition": "Records historical inspiration only; public case truth follows from self-contained stipulated facts.",
            "tag": None,
            "upstream_license": "NOT_APPLICABLE_TO_PUBLIC_GENERALIZATION",
        },
        {
            "canonical_repository": "https://github.com/meanaverage/spiffe-spire-agent-evals",
            "canonical_url": "https://github.com/meanaverage/spiffe-spire-agent-evals/blob/v0.1.0/corpus/public-regression/0.1.0/role-history.json",
            "content_relationship": "SYNTHETIC_AUTHORING_RECORD",
            "copied_into_repository": True,
            "exact_path": "corpus/public-regression/0.1.0/role-history.json",
            "retrieval_date": RETRIEVED,
            "revision": "v0.1.0",
            "source_id": "synthetic-contrastive-authoring",
            "source_project": "spiffe-spire-agent-evals",
            "source_sha256": "COMPUTED_AT_RELEASE_VALIDATION",
            "supported_proposition": "Records pair mutations, pre-edit lock, and public-regression lifecycle.",
            "tag": "v0.1.0",
            "upstream_license": "Apache-2.0",
        },
    ]


def build_corpora(args: argparse.Namespace) -> None:
    upstream = load(args.upstream)
    development = load(args.development)
    contrastive = load(args.contrastive)
    output = args.output
    ledger: list[dict[str, Any]] = []

    groups: list[tuple[str, dict[str, Any], list[dict[str, Any]]]] = []

    upstream_cases = []
    for scenario in upstream["scenarios"]:
        meta = UPSTREAM_META[scenario["id"]] | {
            "origin": UPSTREAM_META[scenario["id"]]["strength"],
            "transformation": "Original benchmark scenario paraphrased from the pinned sources; no upstream source excerpt copied.",
        }
        case, provenance = clean_case(scenario, "UPSTREAM_SPECIFICATION_BOUNDED_DERIVED", meta)
        upstream_cases.append(case)
        ledger.append(provenance)
    groups.append(("upstream", upstream, upstream_cases))

    development_cases = []
    for scenario in development["scenarios"]:
        base = DEVELOPMENT_META[scenario["id"]]
        meta = base | {
            "strength": "DERIVED",
            "origin": "PRIVATE_DERIVED",
            "kind": "PRIVATE_DERIVED",
            "transformation": "Product-neutral generalization from independently adjudicated private review; all private product/repository/schema details removed and public truth limited to stipulated facts.",
        }
        case, provenance = clean_case(scenario, "DEVELOPMENT_REGRESSION", meta)
        development_cases.append(case)
        ledger.append(provenance)
    groups.append(("development-regression", development, development_cases))

    counterpart = {}
    for pair in PAIR_META.values():
        left, right = pair["cases"]
        counterpart[left] = right
        counterpart[right] = left
    contrastive_cases = []
    for scenario in contrastive["scenarios"]:
        pair = PAIR_META[scenario["pair_id"]]
        sources_for_case = ["synthetic-contrastive-authoring", "benchmark-claim-strength-policy"]
        if scenario["pair_id"] in {
            "caller-supplied-attribute",
            "detached-evidence-freshness",
            "spiffe-id-role-classification",
        }:
            sources_for_case.append("spiffe-id-spec")
        meta = {
            "format": scenario["implementation_idiom"],
            "strength": "DERIVED",
            "origin": "DERIVED",
            "kind": "SYNTHETIC_MUTATION",
            "paired_case": counterpart[scenario["id"]],
            "sources": sources_for_case,
            "rationale": CONTRASTIVE_RATIONALE[scenario["id"]],
            "sufficiency": "Expected strength follows from explicit scenario facts, the published claim lattice, and the recorded decisive pair mutation; it is not a discovered upstream vulnerability.",
            "transformation": "Original product-neutral synthetic scenario authored after diagnosis of the first ablation and locked before the tested skill wording change.",
            "mutation": pair["decisive_mutation"],
        }
        case, provenance = clean_case(scenario, "CONTRASTIVE", meta)
        contrastive_cases.append(case)
        ledger.append(provenance)
    groups.append(("contrastive", contrastive, contrastive_cases))

    for name, original, cases in groups:
        envelope = {
            "$schema": "../../../schemas/case-v1.json",
            "corpus_role": PUBLIC_ROLE,
            "corpus_version": CORPUS_VERSION,
            "description": original.get("description", "Public regression cases."),
            "scenario_count": len(cases),
            "scenarios": cases,
            "subgroup": cases[0]["metadata"]["subgroup"],
        }
        dump(output / "corpus" / "public-regression" / CORPUS_VERSION / f"{name}.json", envelope)

    pair_records = []
    for pair_id, item in sorted(PAIR_META.items()):
        record = {
            "case_ids": item["cases"],
            "decisive_mutation": item["decisive_mutation"],
            "irrelevant_difference_assessment": "No case ID, pair role, benign/defect label, or expected answer is included in prompt-visible material. The stated differences implement the security-relevant control under test.",
            "integrity": item["integrity"],
            "pair_id": pair_id,
            "prompt_leaks_pair_role": False,
        }
        if "caveat" in item:
            record["caveat"] = item["caveat"]
        pair_records.append(record)
    dump(
        output / "corpus" / "public-regression" / CORPUS_VERSION / "pair-integrity.json",
        {"corpus_version": CORPUS_VERSION, "pair_count": 6, "pairs": pair_records},
    )
    dump(
        output / "corpus" / "public-regression" / CORPUS_VERSION / "role-history.json",
        {
            "current_role": PUBLIC_ROLE,
            "disclosure_rule": "These cases must never again support an unseen-evidence claim.",
            "historical_corpus_sha256": "468cb60412cb74a9d2a1165b72245ab7c6f13e92b10b0a1aa9bc95e698e82b8e",
            "historical_holdout_lock_sha256": "3c297c739cc62b100a88887309acda3b3e676f3574aef1cab2cda3f38dd21432",
            "pair_count": 6,
            "previous_role_at_execution": "UNRELEASED_GENERALIZATION_HOLDOUT",
            "scenario_count": 12,
            "status_at_execution": "unseen and locked before the tested skill edit",
            "transition": "frozen experiment -> disclosure -> PUBLIC_REGRESSION_V0",
        },
    )
    source_records = sources()
    for record in source_records:
        if record["source_sha256"] == "COMPUTED_AT_RELEASE_VALIDATION":
            local_source = output / record["exact_path"]
            if local_source.is_file():
                record["source_sha256"] = hashlib.sha256(local_source.read_bytes()).hexdigest()
    dump(
        output / "provenance" / "sources.json",
        {"retrieval_date": RETRIEVED, "schema": "spiffe-spire-agent-evals-sources/v1", "sources": source_records},
    )
    dump(
        output / "provenance" / "cases.json",
        {
            "case_count": len(ledger),
            "cases": sorted(ledger, key=lambda item: item["case_id"]),
            "corpus_version": CORPUS_VERSION,
            "schema": "spiffe-spire-agent-evals-case-provenance/v1",
        },
    )


def numeric_grade(grade: dict[str, Any]) -> dict[str, Any]:
    return {
        "authority_correctness": grade["authority_correctness"],
        "boundary_correctness": grade["boundary_correctness"],
        "claim_label_consistency": grade["claim_label_consistency"],
        "contradictory_label": grade["contradictory_label"],
        "false_positive_discipline": grade["false_positive_discipline"],
        "overclaim": grade["overclaim"],
        "semantic_correctness": grade["semantic_correctness"],
        "underclaim": grade["underclaim"],
    }


def build_results(args: argparse.Namespace) -> None:
    score = load(args.scores)
    manifest = load(args.manifest)
    result_by_run: dict[str, dict[str, Any]] = {}
    for path in args.runs.glob("*/*/result.json"):
        record = load(path)
        if record.get("status") == "ok":
            result_by_run[record["run_id"]] = record
    rows = sorted(
        score["scored_samples"],
        key=lambda item: (
            item["corpus"], item["scenario_id"], item["provider"],
            item["condition"], item["repeat"],
        ),
    )
    grades = []
    hashes = []
    case_accumulator: dict[tuple[str, str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for index, item in enumerate(rows, 1):
        result = result_by_run[item["run_id"]]
        sample_id = f"S{index:04d}"
        public_corpus = PUBLIC_ROLE if item["corpus"] == "holdout" else "DEVELOPMENT_REGRESSION"
        grades.append(
            {
                "condition": item["condition"],
                "corpus_role": public_corpus,
                "grader_scores": {
                    name: numeric_grade(value)
                    for name, value in sorted(item["grader_scores"].items())
                },
                "mean_base_total": item["mean_base_total"],
                "mean_scores": item["mean_scores"],
                "repeat": item["repeat"],
                "sample_id": sample_id,
                "scenario_id": item["scenario_id"],
                "target_configuration_id": item["provider"],
            }
        )
        hashes.append(
            {
                "condition": item["condition"],
                "corpus_role": public_corpus,
                "raw_response_sha256": result["raw_response_sha256"],
                "repeat": item["repeat"],
                "request_sha256": result["request_sha256"],
                "sample_id": sample_id,
                "scenario_id": item["scenario_id"],
                "target_configuration_id": item["provider"],
            }
        )
        case_accumulator[(public_corpus, item["scenario_id"], item["provider"], item["condition"])].append(item)

    case_scores = []
    for key, items in sorted(case_accumulator.items()):
        corpus_role, scenario_id, provider, condition = key
        case_scores.append(
            {
                "condition": condition,
                "corpus_role": corpus_role,
                "mean_base_total": round(sum(item["mean_base_total"] for item in items) / len(items), 4),
                "mean_dimensions": {
                    dimension: round(sum(item["mean_scores"][dimension] for item in items) / len(items), 4)
                    for dimension in sorted(items[0]["mean_scores"])
                },
                "response_count": len(items),
                "scenario_id": scenario_id,
                "target_configuration_id": provider,
            }
        )

    result_root = args.output / "results" / "v0.1"
    dump(
        result_root / "grades.numeric.json",
        {"grade_count": len(grades) * 2, "response_count": len(grades), "responses": grades, "schema": "spiffe-spire-agent-evals-numeric-grades/v1"},
    )
    dump(
        result_root / "response-hashes.json",
        {"hash_kind": "raw response bytes as recorded by the frozen harness", "response_count": len(hashes), "responses": hashes, "schema": "spiffe-spire-agent-evals-response-hashes/v1"},
    )
    dump(
        result_root / "case-scores.json",
        {"aggregates": case_scores, "schema": "spiffe-spire-agent-evals-case-scores/v1"},
    )
    dump(
        result_root / "scores.json",
        {
            "condition_aggregates": score["condition_aggregates"],
            "corpus_accounting": score["corpus_accounting"],
            "graders": score["graders"],
            "inter_rater": score["inter_rater"],
            "paired_condition_contrasts": score["paired_contrasts"],
            "scenario_aggregates": score["scenario_aggregates"],
            "schema": "spiffe-spire-agent-evals-scores/v1",
            "score_method": score["score_method"],
        },
    )
    run_manifest = {
        "claim_limits": manifest["claim_limits"],
        "corpus_version": CORPUS_VERSION,
        "evaluation_date_utc": manifest["evaluation_date_utc"],
        "generic_security_control": manifest["generic_security_control"] | {
            "control_text_path": "WITHHELD_RIGHTS_NOT_ESTABLISHED",
            "control_text_publication": "DIGEST_AND_METADATA_ONLY",
            "license": "NOT_RECORDED",
        },
        "grader_disagreement_handling": manifest["grader_disagreement_handling"],
        "grader_prompt": manifest["grader_prompt"],
        "graders": manifest["graders"],
        "missing_reproducibility_fields": manifest["missing_before_fully_reproducible_public_claim"],
        "raw_response_policy": "PUBLISH_HASHES_AND_SCORES_ONLY",
        "result_id": "2026-09-04-frozen-v1",
        "runner_version": "0.1.0-public-interface; frozen private harness identified by digest only",
        "schema": "spiffe-spire-agent-evals-run-manifest/v1",
        "scorer_version": "0.1.0",
        "target_generation": manifest["target_generation"],
        "tested_conditions": manifest["tested_conditions"],
        "transport_and_retry": manifest["benchmark"]["transport_and_retry"],
    }
    dump(result_root / "run-manifest.json", run_manifest)
    dump(
        args.output / "prompts" / "prompts.json",
        {
            "grader_system_prompt": {
                "bytes": len(GRADER_SYSTEM_PROMPT.encode("utf-8")),
                "sha256": sha256_text(GRADER_SYSTEM_PROMPT),
                "text": GRADER_SYSTEM_PROMPT,
            },
            "schema": "spiffe-spire-agent-evals-prompts/v1",
            "target_system_prompt": {
                "bytes": len(TARGET_SYSTEM_PROMPT.encode("utf-8")),
                "sha256": sha256_text(TARGET_SYSTEM_PROMPT),
                "text": TARGET_SYSTEM_PROMPT,
            },
        },
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--upstream", type=Path, required=True)
    parser.add_argument("--development", type=Path, required=True)
    parser.add_argument("--contrastive", type=Path, required=True)
    parser.add_argument("--scores", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--runs", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    build_corpora(args)
    build_results(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
