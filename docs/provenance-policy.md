# Provenance policy

Ground truth must be supported independently of model judgments. “A model said
so” and cross-model agreement are never sufficient authority.

Accepted ground-truth strengths are:

- `AUTHORITATIVE`: official specification, advisory, exact upstream behavior,
  source, or test directly establishes the expected result;
- `STRONG`: exact upstream history/source plus corroborating test or fix
  evidence;
- `DERIVED`: a bounded synthetic scenario whose outcome follows from explicit
  facts and authoritative boundary semantics; and
- `PRIVATE_DERIVED`: product-neutral material historically inspired by private
  integration evidence. Only self-contained generalized facts may publish, and
  the private origin must remain visible.

Each case records a fixture digest, source IDs, immutable revisions and paths
where applicable, transformation method, source relationship, upstream
license, rationale, and sufficiency statement. Synthetic pairs additionally
record the exact decisive mutation and why unrelated differences do not decide
the answer.

Fixture relationships are:

- `EXACT_UPSTREAM`
- `MINIMALLY_EXTRACTED`
- `SYNTHETIC_MUTATION`
- `PRIVATE_DERIVED`

Prefer immutable provenance plus deterministic verification over copied source.
If an exact excerpt is necessary, retain upstream notices and record changes.
Changing ground truth, thresholds, or a material source interpretation requires
a new corpus version.
