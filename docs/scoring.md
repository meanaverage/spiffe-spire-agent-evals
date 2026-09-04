# Scoring contract

Scorer version: 0.1.0

## Headline score

Each response receives four integer dimensions from 0–2. The two blinded
graders are averaged equally per dimension; the four averaged dimensions are
summed per response and then arithmetically averaged for a result cell.

### 1. Semantic correctness

- 2 — reaches all material expected conclusions without contradiction.
- 1 — directionally correct but misses a material lifecycle/security
  distinction.
- 0 — materially wrong or recommends an unsafe semantic conclusion.

### 2. Authority correctness

- 2 — identifies the appropriate source class and exact version/path when the
  scenario supplies one.
- 1 — cites credible upstream authority but loses material version/path
  specificity.
- 0 — relies on generic/community advice despite available authority, or
  invents evidence.

### 3. Boundary correctness

- 2 — separates SPIFFE/SPIRE/client behavior from deployment integration and
  application policy.
- 1 — reaches a safe conclusion but leaves ownership vague.
- 0 — materially attributes application authorization/effect semantics to
  SPIFFE/SPIRE or otherwise crosses the boundary.

### 4. False-positive discipline

- 2 — avoids every `must_not` conclusion and clearly labels uncertainty.
- 1 — avoids dangerous conclusions but includes unsupported speculation or
  overstatement.
- 0 — asserts a forbidden/unsupported conclusion or weakens
  trust/verification without evidence.

The headline range is 0–8. It is not certification and should always retain the
per-dimension values.

## Separate consistency score

`claim_label_consistency` is scored 0–2 and is not added to the /8 total:

- 2 — narrative, present/missing evidence, and labels are materially
  consistent;
- 1 — imprecise, but no label asserts a prerequisite the narrative clearly
  denies; and
- 0 — material internal contradiction.

Consistency is internal to the response. A confidently wrong but internally
consistent response is a semantic error, not automatically a consistency
error. A contradictory label includes calling something a demonstrated bypass
while saying reachability/effect evidence is missing, calling it exploitable
without a plausible actor/control path, or returning non-finding while its own
narrative establishes an owning-boundary invariant failure.

## Diagnostic flags

- `overclaim`: strongest material conclusion exceeds supplied evidence or the
  expected claim.
- `underclaim`: response fails to retain an expected invariant violation or
  bypass.
- `contradictory_label`: narrative and final label contradict internally; this
  is not merely disagreement with ground truth.
- `benign_false_positive`: `overclaim` among the five primary cases whose first
  expected claim is `non_finding`—15 responses per target/condition.
- `positive_underclaim`: `underclaim` among the seven primary cases whose first
  expected claim is not `non_finding`—21 responses per target/condition. This
  includes both `invariant_violation` and `demonstrated_bypass` truth.

Boolean headline percentages are equal-weight mean-judge rates. Publication
must also retain each grader's rate plus both-grader and either-grader rates.

Other useful diagnostics include vulnerable-case detection where applicable,
patched/benign-twin discrimination, per-pair score/label contrast, and
context-dependent calibration. V0.1.0 contains synthetic semantic twins, not
historical upstream vulnerable/patched source revisions.

## Claim-strength model

The evidence hierarchy is:

1. `SUSPECTED`: plausible concern; a decisive prerequisite is missing.
2. `INVARIANT_VIOLATION`: supplied source/facts establish a required property
   fails, even if attacker control is unproven.
3. `EXPLOITABLE_VULNERABILITY`: plausible actor/control path can turn the
   violation into unauthorized effect.
4. `DEMONSTRATED_BYPASS`: reproducible actor-controlled path reaches the
   protected effect contrary to policy.

Do not promote a claim without its prerequisites. Do not demote a proven
invariant merely because exploitability is unproven.
