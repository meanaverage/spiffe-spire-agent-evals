# Result reporting and versioning

Every result identifies exact corpus, scorer, rubric, runner, response/grade
schema, model configuration, treatment, and treatment content revision/digest.
Missing fields use `UNKNOWN` or `NOT_RECORDED`.

Version surfaces independently:

| Surface | Initial version | Change rule |
|---|---|---|
| Corpus | 0.1.0 | New cases are a minor release; changed truth/labels/thresholds require a new score-affecting corpus version. |
| Scorer/rubric | 0.1.0 | Changed dimension meaning, flags, weighting, denominators, or aggregation requires a new version. |
| Runner | 0.1.0 | Changed prompt construction or adapter behavior that can alter output requires a new version. |
| Schemas | v1 | Breaking field or meaning changes require a new schema ID. |
| Result set | `2026-09-04-frozen-v1` | Immutable; corrections publish a successor and preserve this record. |

Public-regression and independently held-out performance are distinct result
classes. A leaderboard must not rank family names without exact configuration,
must publish every registered condition rather than favorable subsets, and
must preserve negative or regression results for first-party systems.

Do not silently rewrite released result JSON. A release tag identifies exact
bytes; later clarification belongs in a new version and changelog.
