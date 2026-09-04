# Implementation independence

This benchmark is implementation-neutral. Any prompt, model, agent, or skill
that emits the public response schema may participate.

`spiffe-spire-agent-skill` is one evaluated system. It is not required, does
not define benchmark ground truth, and receives no protected reporting status.
Results are preserved when another skill, generic guidance, or no guidance
performs better. Negative results and regressions for the first-party skill are
part of the historical record.

Ground truth is governed here, independently of any evaluated system. Skill
changes never update case truth automatically. Benchmark changes do not
redefine a skill's behavior. A headline case or ground-truth change requires a
reviewer other than the author of the evaluated-system change it targets.

Scores are not certification and do not prove general security competence.
