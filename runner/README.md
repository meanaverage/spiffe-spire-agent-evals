# Public runner

Runner version: 0.1.0

The runner is intentionally provider-neutral and standard-library-only. It
selects a case by ID, copies only `prompt_visible`, verifies the fixture digest,
adds an explicitly named condition packet, records request/response digests,
and invokes one caller-supplied adapter command.

The adapter receives one JSON request on stdin and must write the target's JSON
response to stdout. Provider credentials, URLs, and topology stay in the
adapter environment. They are not configuration fields in this repository.

There are no automatic retries. A transport retry must be a new, explicitly
recorded invocation. Success and failure have different files. Runtime outputs
go under ignored `.runs/`; they are not automatically publication-safe.

This runner does not implement native agent-skill loading in v0.1.0. A future
native-skill adapter must use a distinct delivery-mode label and must preserve
the target/ground-truth isolation boundary.
