# Holdout and public-regression policy

## PUBLIC_REGRESSION

Public cases support reproducibility, debugging, comparison, and regression
testing. Authors and models may know them. Public-case performance must not be
presented as unseen generalization evidence.

The 12 contrastive cases in v0.1.0 were unseen and locked when the frozen
2026-09-04 experiment ran. Disclosure graduates them to
`PUBLIC_REGRESSION_V0`; the historical status may be reported only as “unseen
at execution.”

## UNRELEASED_GENERALIZATION_HOLDOUT

An unreleased generalization holdout is retained outside public Git history,
branches, issues, pull requests, CI artifacts, model-accessible filesystems,
and evaluated-system workspaces. It is unavailable to skill/model authors
during tuning. After a frozen experiment and disclosure, it may graduate into
a later public-regression release and must be replaced.

This repository contains no unreleased holdout content. No replacement holdout
was inventoried at v0.1.0. One must be created and locked outside this public
repository before future tuning or generalization claims.

## Contamination and reporting

Public GitHub benchmarks may enter training corpora or model context over time.
Leaderboards must label `PUBLIC_REGRESSION` and independently held-out results
separately. Prompt memorization and direct tuning against public cases are
expected risks, not evidence of misconduct; they simply limit what a public
score can claim.

Corpus releases are immutable. Disclosure status is monotonic: a public case
never becomes unseen again.
