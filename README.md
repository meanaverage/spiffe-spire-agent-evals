# spiffe-spire-agent-evals

Independent, provenance-grounded evaluations for AI reasoning about
SPIFFE/SPIRE security, integration, and operational behavior.

> **This benchmark is implementation-neutral.**
> [`spiffe-spire-agent-skill`](https://github.com/meanaverage/spiffe-spire-agent-skill)
> is one evaluated system; using that skill is not required. Results may show
> that another skill, generic guidance, or no skill performs better. Negative
> and regression results for the first-party skill are preserved.

## Frozen result

The initial release records a 2026-09-04 deterministic
skill-content-packet evaluation. It used 12 contrastive cases that were unseen
and locked at execution, plus three separately reported development-regression
cases. The contrastive cases are public now and have graduated to
`PUBLIC_REGRESSION_V0`; they cannot support future unseen-evidence claims.

| Compact recorded target configuration | No skill | Generic control | SPIFFE/SPIRE base | Base + adjudicated revised |
|---|---:|---:|---:|---:|
| Self-hosted served alias `qwen38-27b-dflash2` · SGLang · NVFP4 · `dflash2` · TP2 · no-think · temp 0 · max 1,800 | 5.333 | 7.069 | 5.569 | **7.500** |
| OpenAI `gpt-5.6-sol` · Codex CLI 0.151.0 · reasoning `medium` · ephemeral/read-only | 7.597 | 7.847 | 7.236 | **7.972** |

The /8 headline is the sum of semantic, authority, boundary, and
false-positive-discipline scores (0–2 each). Under the revised packet, Qwen
claim-label consistency was 1.944/2 with mean-judge overclaim 2.78%, underclaim
0%, contradictory label 0%, benign FP 6.67%, and positive underclaim 0%. The
OpenAI revised condition recorded 2.000/2 consistency and 0% on all five
headline Boolean error rates.

For the Qwen-target/base benign cases, grader disagreement was substantial:
0% benign FP from the Qwen grader and 100% from the OpenAI grader produced the
50% mean-judge result. Under revised, 0% and 13.33% produced 6.67%. Boolean
means are not third-adjudicated event rates.

The Qwen identifier is only a served alias; upstream model identity and
immutable weights were not recorded. Its requests also set
`chat_template_kwargs.enable_thinking=false`, required strict JSON-schema
output, and supplied no tools or browser. The OpenAI target used `codex exec
--ephemeral`, an isolated working directory, ignored user configuration and
workspace rules, a read-only sandbox, a strict frozen output schema, a prompt
prohibiting tools/browsing, and recorded zero target tool events. For OpenAI,
temperature, `top_p`, seed, maximum output, service-side immutable revision,
and exact network policy were not recorded. The results apply only to these
configurations, treatment bytes, corpus, and graders. They are not
certification or evidence of general model superiority.

The revised packet was tested at skill revision
`569e98164e64c6e1d7632511895e44a4d6e0a641`; it is distinct from the accepted
squash-merge integration commit
`12992f03b2489c18dfae856cfec9cd0b9fd0354f`. The 12 packet files match that
integration commit by SHA-256.

[Full historical report](results/v0.1/report.md) ·
[Run manifest](results/v0.1/run-manifest.json) ·
[Scores](results/v0.1/scores.json) ·
[Response hashes](results/v0.1/response-hashes.json)

## What was actually tested

There were four conditions: no skill, a generic security-review control added
to the base packet, the SPIFFE/SPIRE base packet, and base plus adjudicated
guidance. For every skill-bearing condition, the harness deterministically
concatenated `SKILL.md` and every Markdown reference into one prompt packet.
All references were visible on every request. Native skill loading, filesystem
discovery, routing, and progressive disclosure were not tested.

The run contained 288 primary plus 72 development-regression responses. Both
model graders scored every response: 720 grades in 60 calls. There was no third
grader. See the [methodology](docs/methodology.md) for configurations,
blinding, agreement, limitations, and treatment construction.

## Corpus

Corpus version 0.1.0 contains exactly 23 public cases:

| Subgroup | Cases | Ground-truth provenance |
|---|---:|---|
| Upstream/specification/bounded-derived baseline | 8 | 6 `AUTHORITATIVE`, 2 `DERIVED` |
| Development regression | 3 | `DERIVED` truth with explicit `PRIVATE_DERIVED` origin |
| Contrastive semantic twins | 12 | `DERIVED` synthetic mutations in 6 pairs |

Every case separates `prompt_visible` from `ground_truth`, records stable IDs
and fixture/case digests, and resolves to the [per-case provenance
ledger](provenance/cases.json). The public runner selects only prompt-visible
material. Because all case truth is public, these are regression cases rather
than an unseen holdout.

## Scoring

The [scoring contract](docs/scoring.md) versions four headline dimensions,
separate claim-label consistency, overclaim/underclaim/contradiction flags, and
the exact benign/positive denominators. A confidently wrong but internally
consistent answer is semantically wrong; it is not automatically a consistency
failure.

Claim strength follows:

`SUSPECTED` → `INVARIANT_VIOLATION` → `EXPLOITABLE_VULNERABILITY` → `DEMONSTRATED_BYPASS`

Do not promote without prerequisites or demote a proven invariant merely
because exploitability remains unproven.

## Reproduce and validate

Python 3.11+ and the standard library are sufficient:

```bash
python -m unittest discover -s tests -v
python scoring/validate.py
python scoring/aggregate.py results/v0.1/grades.numeric.json
```

The [public runner](runner/README.md) accepts a caller-supplied command adapter
without embedding provider endpoints or credentials. It intentionally selects
one named case rather than giving an agent recursive repository access.

## Provenance and licensing

The [source ledger](provenance/sources.json) pins authoritative SPIRE,
go-spiffe, and SPIFFE specification revisions, paths, and blob SHA-256 values.
No upstream source file is copied; cases use original paraphrases or synthetic
facts. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

The repository's original material is Apache-2.0. The generic-control text's
standalone authorship/license was `NOT_RECORDED`, so v0.1.0 publishes its exact
digest and role but withholds the bytes. Raw target/grader prose is also
withheld; the release follows `PUBLISH_HASHES_AND_SCORES_ONLY`.

## Holdout policy

This repository contains no `UNRELEASED_GENERALIZATION_HOLDOUT`. A replacement
must be created and governed outside public GitHub before any future tuning or
generalization claim. Public GitHub cases may enter model training data over
time. Read the [holdout policy](docs/holdout-policy.md).

## Independence and governance

The skill repository does not define benchmark truth. Ground-truth and scoring
changes are independently reviewed and versioned; all registered conditions
and unfavorable results remain in history. See
[implementation independence](docs/independence.md),
[governance](docs/governance.md), and the
[model-reporting policy](docs/model-reporting.md).
