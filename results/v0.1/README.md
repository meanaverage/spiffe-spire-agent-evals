# Frozen result v0.1

Result ID: `2026-09-04-frozen-v1`

Versions: corpus 0.1.0, scorer 0.1.0, public runner interface 0.1.0.

This directory publishes the historical report, exact public-safe run
configuration, aggregate and per-case scores, per-response numeric/Boolean
grades, and request/response hashes. Raw target responses, raw grader prose,
private blind mappings, logs, and internal deployment metadata are absent under
`PUBLISH_HASHES_AND_SCORES_ONLY`.

The public runner is a sanitized interface and was not the original execution
harness. The exact frozen private harness is identified in the run manifest by
digest; do not imply that a new run through runner 0.1.0 reproduces service-side
model state.

See [report.md](report.md), [run-manifest.json](run-manifest.json), and the
repository [reproduction guide](../../docs/reproduction.md).
