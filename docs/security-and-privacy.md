# Publication security and privacy

Public artifacts use an allowlist. They may contain stable public sample IDs,
case/corpus versions, public model configuration, condition IDs and digests,
prompt/fixture/response hashes, numeric/Boolean grades, aggregate results,
publication-safe timestamps, and public failure categories.

They must not contain credentials, credential locations, private endpoints,
host or VM names, user or home paths, private repository paths, internal
deployment/run identifiers, network topology, environment variables, customer
data, operational logs, stderr/event streams, or hidden holdout mappings.

Raw target and grader prose is withheld in v0.1.0 because redistribution review
was not recorded. Publication contains hashes and scores only. The original
frozen material is retained privately for a possible later rights-reviewed,
sanitized, separately versioned artifact.

Report suspected publication-safety issues privately to repository maintainers
before opening a public issue containing sensitive details.
