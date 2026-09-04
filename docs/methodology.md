# Methodology

Version: 0.1.0

## What the benchmark measures

Cases test whether a response reaches supported SPIFFE/SPIRE security and
integration conclusions, chooses appropriate authority, respects the boundary
between workload identity and relying-application policy, avoids unsupported
findings, and keeps claim labels consistent with its own evidence narrative.
The benchmark does not execute SPIRE and is not security certification.

`PUBLIC_REGRESSION_V0` contains 23 cases:

- eight upstream/specification and bounded-derived baseline cases;
- three `PRIVATE_DERIVED`-origin development-regression cases; and
- 12 synthetic contrastive cases in six semantic-twin pairs.

The development-regression group is reported separately and never contributes
to the frozen primary score.

## Frozen 2026-09-04 design

The 12 contrastive cases were authored after diagnosis of an earlier ablation,
then locked before the tested skill wording change. They were unseen at
execution. They are public regression data now and cannot support future unseen
generalization claims.

Each target/condition/case had three observed repetitions. There were four
conditions and two exact target configurations, producing 288 primary and 72
development-regression responses (360 total). Temperature-zero repetitions are
observations, not guaranteed independent statistical trials.

Conditions were:

1. `NO_SKILL`
2. `GENERIC_SECURITY_CONTROL`
3. `SPIFFE_SPIRE_BASE`
4. `BASE_PLUS_ADJUDICATED_REVISED`

This was a deterministic skill-content-packet evaluation. For every
skill-bearing condition, the harness concatenated `SKILL.md` and every Markdown
reference into one prompt packet, so every reference was visible on every
request. Native skill loading, filesystem skill discovery, routing, and
progressive disclosure were not tested.

The generic control added non-SPIFFE-specific security-review guidance to the
complete base packet. Its addition was 12,393 bytes / 1,673
whitespace-delimited words. The combined packet was 38,319 bytes / 4,971 words,
versus 40,370 bytes / 5,167 words for the revised packet. Tokenizer-token counts
were `NOT_RECORDED`. The generic text itself is withheld because standalone
authorship/license evidence was not recorded.

## Target context and contamination boundary

Target context contained the 648-byte reviewer instruction, prompt-visible case
text, condition packet, and strict response schema. It omitted `expected`,
`must_not`, `authority`, `finding_threshold`, and `expected_claims` fields.
Qwen had no tool/browser interface. Codex was instructed not to use tools or
inspect files and recorded zero tool events.

For a public repository, human readers necessarily can see ground truth. The
runner therefore loads a named case and explicitly selects only
`prompt_visible`; it never gives an agent a repository path or recursively
loads corpus/provenance files. Public-case scores remain regression evidence,
not hidden-evidence measurements.

## Exact target configurations

### Served alias `qwen38-27b-dflash2`

- self-hosted SGLang through an OpenAI-compatible chat-completions API;
- NVFP4;
- `dflash2` build/kernel tag;
- tensor parallelism 2;
- thinking disabled with `chat_template_kwargs.enable_thinking=false`;
- temperature 0;
- maximum output 1,800 tokens;
- strict JSON-schema output; and
- no tools or browser interface supplied.

The underlying upstream model identity, immutable weights revision/hash, exact
quantization recipe, SGLang version/commit, `dflash2` definition,
kernels/drivers/accelerator, omitted sampler defaults, and seed were `UNKNOWN`
or `NOT_RECORDED` as specified in the run manifest.

### OpenAI `gpt-5.6-sol`

- Codex CLI 0.151.0;
- reasoning effort `medium`;
- `codex exec --ephemeral`;
- isolated working directory per sample;
- ignored user configuration/workspace rules;
- read-only sandbox;
- strict frozen output schema;
- prompt prohibited tools/browsing; and
- zero observed target tool events.

Temperature, `top_p`, seed, maximum output, service-side immutable model
revision, and exact sandbox network policy were `NOT_RECORDED`.

Both targets received the same reviewer instruction text: as a system message
for Qwen and concatenated on stdin for Codex.

## Grading

Every response was blindly scored by both the served alias
`qwen38-27b-dflash2` (no-think, temperature 0, max 8,000) and OpenAI
`gpt-5.6-sol` via Codex CLI 0.151.0 (medium reasoning, ephemeral/read-only).
Each grader saw the rubric, full scenario ground truth, and 12 anonymous
responses. Provider, condition, repetition, and run identifiers were withheld;
prose could still carry stylistic/reference clues. Each grader scored 180
outputs from its own model identifier while blinded to that identity.

There were 720 response-level grades in 60 calls. No third grader adjudicated
disagreement. Numeric dimensions were averaged equally. Boolean output retains
per-grader, both-grader, either-grader, and mean-judge rates.

Across 1,800 dimension comparisons, exact agreement was 82.44% and mean
absolute difference was 0.1878 on the 0–2 scale. Boolean disagreement was
material in some cells: on Qwen-target/base benign cases the Qwen grader
reported 0% benign FP and the OpenAI grader 100%, yielding 50% mean-judge; on
revised, the rates were 0% and 13.33%, yielding 6.67%.

## Execution and isolation limitations

- Actual target/grader worker counts and exact invocation lines were not frozen.
- No automatic target or grader retry existed, and no retry artifact was
  observed; unrecorded successful manual re-execution cannot be excluded.
- Zero tool use was observed, but hard filesystem/network inaccessibility of
  every benchmark artifact was not cryptographically established.
- Immutable model/backend identity and several serving/sampling fields are
  missing as enumerated in the run manifest.
- Three repetitions and 12 primary cases do not establish statistical or broad
  model superiority.
