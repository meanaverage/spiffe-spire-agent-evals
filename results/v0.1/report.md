# Frozen 2026-09-04 result

This is a historical deterministic skill-content-packet evaluation on 12
contrastive cases that were unseen and locked at execution. They are now
`PUBLIC_REGRESSION_V0`. Three previously used development-regression cases were
rerun separately and are not part of the primary score.

## Primary results

The score sums four 0–2 dimensions for a maximum of 8. Consistency is a
separate 0–2 dimension. Every Boolean percentage is a mean-judge rate, not an
adjudicated event rate.

| Exact recorded target | Condition | Score / 8 | Consistency / 2 | Overclaim | Underclaim | Contradictory label | Benign FP | Positive underclaim |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Served alias `qwen38-27b-dflash2`; SGLang, NVFP4, `dflash2`, TP2, no-think, temp 0, max 1,800 | No skill | 5.333 | 0.972 | 43.06% | 26.39% | 30.56% | 50.00% | 38.10% |
| Same served configuration | Generic security control | 7.069 | 1.778 | 9.72% | 6.94% | 4.17% | 16.67% | 4.76% |
| Same served configuration | SPIFFE/SPIRE base | 5.569 | 0.972 | 45.83% | 23.61% | 31.94% | 50.00% | 38.10% |
| Same served configuration | Base + adjudicated guidance | **7.500** | **1.944** | **2.78%** | **0.00%** | **0.00%** | **6.67%** | **0.00%** |
| OpenAI `gpt-5.6-sol`; Codex CLI 0.151.0, reasoning `medium`, ephemeral/read-only | No skill | 7.597 | 1.750 | 13.89% | 0.00% | 11.11% | 0.00% | 0.00% |
| Same OpenAI configuration | Generic security control | 7.847 | 1.972 | 4.17% | 0.00% | 0.00% | 0.00% | 0.00% |
| Same OpenAI configuration | SPIFFE/SPIRE base | 7.236 | 1.708 | 26.39% | 0.00% | 11.11% | 13.33% | 0.00% |
| Same OpenAI configuration | Base + adjudicated guidance | **7.972** | **2.000** | **0.00%** | **0.00%** | **0.00%** | **0.00%** | **0.00%** |

The Qwen name above is only a served alias; upstream model identity and
immutable weights were not recorded. For OpenAI, temperature, `top_p`, seed,
maximum output, immutable service revision, and exact network policy were not
recorded. These are exact-configuration observations, not family-level model
claims.

Observed revised-minus-base/generic score differences were +1.931/+0.431 for
the Qwen target and +0.736/+0.125 for the OpenAI target. No significance,
causality, or broad superiority claim is made.

Benign-FP disagreement was material for the Qwen target. Under base, the Qwen
grader recorded 0% and the OpenAI grader 100%, producing the 50% mean-judge
rate. Under revised, they recorded 0% and 13.33%, producing 6.67%. Individual,
both/either, and mean-judge values are retained in `scores.json`.

## Development-regression results

| Exact target configuration | No skill | Generic | Base | Revised |
|---|---:|---:|---:|---:|
| Qwen served configuration above | 4.778 | 6.222 | 5.222 | **7.111** |
| OpenAI configuration above | 7.444 | 7.889 | 7.944 | **8.000** |

## Accounting and grading

The run produced 288 primary and 72 development-regression responses. Both
graders scored all 360, yielding 720 response-level grades in 60 calls. Across
1,800 numeric-dimension comparisons, exact agreement was 82.44% and mean
absolute difference was 0.1878 on the 0–2 scale.

Graders saw the rubric, complete scenario truth, and anonymous responses. They
did not receive provider, condition, repetition, or run identifiers, although
prose could reveal clues. Each grader scored 180 outputs from its own model
identifier while blinded. There was no third-grader adjudication.

## Limits

- Native skill loading, filesystem discovery, routing, and progressive
  disclosure were not tested; every Markdown reference was flattened into the
  prompt for skill-bearing conditions.
- The contrastive cases were authored after diagnosis of the first ablation,
  although locked before the tested wording change.
- Three repetitions are observations, not guaranteed independent trials.
- Several immutable model, serving, sampling, invocation, concurrency, and
  isolation details are `UNKNOWN` or `NOT_RECORDED` in the manifest.
- The generic-control text and raw target/grader prose are withheld for
  unresolved publication rights; their hashes/metadata are retained.
- Public-regression scores are not unseen evidence, security certification, or
  proof of general model/security competence.
