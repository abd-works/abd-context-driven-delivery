# Satisfy

Satisfy runs in **tool mode**: it does not inline a recipe. It hands you two tool calls to make yourself, in order — first find the problems, then fix them.

1. **`validate`** — run this first. Judge the artifact under the generator **`active`** root against the **contexts** and every named rule, and call **`scan`** on the session-rooted paths. Produce the full list of violations and coverage gaps. Do not fix anything in this step.
2. **`generate_fixes_from_validate`** — run this second, once you hold the validate report. Follow **`session_guidance`** and edit only under that layout. Generate any missing artifacts (a missing `.context/module-context.md` IS a violation — create it at the current fidelity: thin at modules with Purpose, Seam, Dependencies; full at model with + Primary use case, Rationale, Public API), then fix every reported violation in the same paths — do not invent a divergent folder.

When done, run **`validate`** again and repeat the two-call loop until it passes.
