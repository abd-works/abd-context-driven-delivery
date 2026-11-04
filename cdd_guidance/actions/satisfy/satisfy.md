# Satisfy

One MCP call runs **validate** for every applicable rule on the bound guidance, then appends **generate_fixes_from_validate** instructions. Your job is to apply those fixes in the repo and loop until validate is clean.

1. **Validate (already in this response)** — Judge artifacts under the generator **`active`** root against **contexts** and every named rule. Call **`scan`** on session-rooted paths when the practice provides it. List pass/fail per rule with evidence. Do not skip rules.
2. **Generate fixes (instructions below validate)** — Follow **`session_guidance`** and edit only under that layout. Create missing artifacts (for example `.context/module-context.md` at the current fidelity). Fix every violation validate named. Do not invent a divergent folder.
3. **Fix every format** — A violation is fixed only when every format of the fidelity agrees: its documents, its diagrams, and its code. Fix the same thing in each one (the model markdown, its drawio, and the code it describes), because a fix in one format alone leaves the others still breaking the rule and the formats no longer mirror each other.

When done, run **`validate`** again on the same guidance. Repeat until clean, then report **Fixes**: each file touched and which rule slug each change addressed.
