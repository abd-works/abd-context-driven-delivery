---
description: "When the user corrects generated work, fix the work — do not log the lesson in AGENTS.md"
alwaysApply: true
---

# Learning From Corrections

When the user corrects work you generated, fix the work in the artifact that is wrong. That is the whole job.

**Do not create or update `AGENTS.md` for a correction.** `AGENTS.md` is not a lesson log. Do not add a new file, and do not append a bullet, because the user deleted one. Durable behavior belongs in the source that already governs that work: the module, the test, the skill, or `.context`.

If the same mistake would happen again, change that source so the next run cannot do it. Recording a parallel note in `AGENTS.md` is how those files keep coming back after they are removed.
