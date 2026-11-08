# Satisfy

Satisfy gives you the rules of each listed guidance and the fixes step that follows validate. Your job is to validate, apply the fixes the report names in the repo, and loop until validate is clean.

1. **Validate** — Call **`validate`** with the same guidance. It judges the artifacts against every rule below and saves a report. Call **`scan`** on session-rooted paths when the practice provides it. List pass/fail per rule with evidence. Do not skip rules.
2. **Generate fixes** — Follow **`session_guidance`** and edit only under that layout. Create missing artifacts (for example `.context/module-context.md` at the current fidelity). Fix every violation validate named. Do not invent a divergent folder.
3. **Fix every format** — A violation is fixed only when every format of the fidelity agrees: its documents, its diagrams, and its code. Fix the same thing in each one (the model markdown, its drawio, and the code it describes), because a fix in one format alone leaves the others still breaking the rule and the formats no longer mirror each other.

When done, run **`validate`** again on the same guidance. Repeat until clean, then report **Fixes**: each file touched and which rule slug each change addressed.
