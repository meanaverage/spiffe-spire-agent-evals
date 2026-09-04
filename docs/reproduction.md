# Reproduction

V0.1.0 supports three levels of verification.

## Offline integrity and aggregation

```bash
python -m unittest discover -s tests -v
python scoring/validate.py
python scoring/aggregate.py results/v0.1/grades.numeric.json
```

These commands need only Python 3.11+ and the standard library. They validate
the 23 cases, provenance references, fixture and result digests, pair links,
role policy, privacy/secret patterns, raw-output exclusion, and frozen score
reconstruction.

## Public runner

The runner selects only `prompt_visible` from a named case and combines it with
an explicitly supplied treatment packet. It writes live raw responses under
the ignored `.runs/` directory; publishing those outputs is a separate rights
and privacy decision.

Use a local adapter process that accepts one JSON request on stdin and returns a
schema-conforming response on stdout:

```bash
python -m runner.cli \
  --corpus corpus/public-regression/0.1.0/contrastive.json \
  --case-id holdout-role-exact-classifier \
  --condition-id NO_SKILL \
  --adapter-command './my-adapter' \
  --model-config examples/model-config.example.json
```

For a treatment packet, add `--packet path/to/public-packet.md` and identify
its revision/delivery mechanism in the model configuration. Credentials and
endpoints belong to the adapter's environment, never committed configuration.
The public runner does not implement automatic retries.

## Frozen result reproduction limits

Hashes authenticate the retained 2026-09-04 artifacts but do not make model
execution fully reproducible. The Qwen upstream model/weights and full serving
stack are incomplete; the OpenAI immutable service revision and sampling/output
controls are incomplete; actual worker counts/invocations and hard Codex
network/filesystem isolation were not frozen.

The generic-control text is withheld because its standalone license was not
recorded, so that condition cannot be reconstructed from public bytes in
v0.1.0. Raw target and grader prose is also withheld; hashes and sanitized
numeric/Boolean grades are public. These limits do not prevent offline
verification of published arithmetic, but they prevent a claim of full
external execution reproduction.

Run `python provenance/verify_sources.py` to check pinned external source
digests when network access is available.
