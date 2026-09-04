# Governance

- Corpus truth is owned and versioned in this repository.
- Evaluated systems are peers represented through system manifests.
- Case authors disclose conflicts with evaluated-system work.
- A distinct reviewer approves new headline ground truth.
- Negative, null, and regression results remain published.
- Corrections are new versions with an explanatory changelog; historical result
  files are never silently rewritten.
- External systems use the same public schema, scorer version, and reporting
  requirements.
- The repository does not endorse, certify, or guarantee an evaluated system.

Before release, maintainers verify case/provenance completeness, licensing,
privacy, hashes, schemas, result integrity, and CI. After release, protected tag
or release processes should make accidental mutation conspicuous.
