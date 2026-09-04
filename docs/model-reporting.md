# Model and system reporting policy

Every result row must identify, when known:

- provider and runtime;
- exact served model identifier;
- immutable model/weights revision;
- quantization and serving build;
- reasoning/thinking mode and effort;
- temperature, `top_p`, `top_k`, seed, and other sampling controls;
- maximum output;
- tool/browser and network policy;
- treatment and skill delivery mode;
- treatment content revision/digest;
- runner, corpus, scorer, rubric, and schema versions; and
- repetition, retry, and failure accounting.

Use the literal values `UNKNOWN` and `NOT_RECORDED` rather than inference.
Family names such as “Qwen” or “Codex” are not adequate result identifiers when
configuration affects interpretation.

A native-skill result and a flattened skill-content-packet result are different
treatments and must not share an unqualified label. A public-regression result
must not be labeled held-out.
