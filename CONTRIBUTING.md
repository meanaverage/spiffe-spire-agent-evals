# Contributing

Contributions are welcome from any implementation. Using
`spiffe-spire-agent-skill` is not required.

Case changes must include claim-level provenance, ground-truth rationale,
fixture digests, license status, and an independent reviewer. A contributor who
authored an evaluated system change should not be the only reviewer approving
new headline ground truth for that system.

Result submissions must identify the exact corpus, scorer, runner, treatment,
model configuration, delivery mechanism, and all unknown fields. Submit all
conditions run, including negative or regressing results. Do not select only
favorable outcomes.

Never submit private holdouts, credentials, endpoints, operational logs,
customer data, raw model prose without affirmative redistribution review, or
machine-specific paths. Run:

```bash
python -m unittest discover -s tests -v
python scoring/validate.py
```

Ground-truth, scoring-semantic, and historical-result corrections require a
new version; do not rewrite a published result in place.
