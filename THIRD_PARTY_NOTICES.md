# Third-party notices

This repository uses immutable third-party sources as provenance. It does not
vendor their source files or incorporate model-generated response prose in
v0.1.0. The original benchmark scenarios paraphrase relevant behavior or use
synthetic facts; links and source hashes let reviewers verify the authority.

## SPIRE

- Project: SPIRE, <https://github.com/spiffe/spire>
- Inspected revision: `2f7861ae3923caf1f57eb087fc2928d58c0fb1d2`
- Tag represented: `v1.15.3`
- License: Apache-2.0
- Use: provenance-only references and hashes for selected integration tests;
  no source file is copied.
- License: <https://github.com/spiffe/spire/blob/2f7861ae3923caf1f57eb087fc2928d58c0fb1d2/LICENSE>

## go-spiffe

- Project: go-spiffe, <https://github.com/spiffe/go-spiffe>
- Inspected revision: `e9973f6314a3fa0e36eb1f00fbfe37bdc1554b96`
- Tag represented: `v2.8.1`
- License: Apache-2.0
- Use: provenance-only references and hashes for `workloadapi.X509Source`;
  no source file is copied.
- License: <https://github.com/spiffe/go-spiffe/blob/e9973f6314a3fa0e36eb1f00fbfe37bdc1554b96/LICENSE>

## SPIFFE specifications

- Project: SPIFFE specifications, <https://github.com/spiffe/spiffe>
- Inspected revision: `99470b9abc825f14aa364dfa2c3b53b02ba5db5b`
- License: Apache-2.0
- Use: provenance-only references and hashes for SPIFFE ID, trust-domain,
  Workload API, and X.509-SVID semantics; no specification file is copied.
- License: <https://github.com/spiffe/spiffe/blob/99470b9abc825f14aa364dfa2c3b53b02ba5db5b/LICENSE>

## spiffe-spire-agent-skill

- Project: spiffe-spire-agent-skill,
  <https://github.com/meanaverage/spiffe-spire-agent-skill>
- Tested revisions: `fbf9d2751a526f4f0ab059fa14facd942571cc5f`
  and `569e98164e64c6e1d7632511895e44a4d6e0a641`
- License: Apache-2.0
- Use: one evaluated system. Skill packet bytes are not copied; condition
  records contain revisions, file lists, and digests for reconstruction.

## Generic security control

The generic-control text used by the frozen experiment has SHA-256
`a40a05d76f6dbba471e718b9db7c64c5c07870320ec0267f80f9e3f78d210ccc`.
Its authorship and standalone license were `NOT_RECORDED` in the frozen
publication evidence. The text is therefore withheld from this release. Its
digest, byte/word counts, non-SPIFFE-specific role, and combined-packet digest
are retained for historical interpretation. Apache-2.0 does not relicense the
withheld artifact.

## Model outputs

Raw target responses and raw grader output are not distributed in v0.1.0.
Response hashes, numeric/Boolean grades, and aggregate statistics are provided.
This repository's Apache-2.0 license does not assert ownership of or relicense
the omitted outputs.
