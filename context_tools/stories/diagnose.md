# Diagnose (Stories)

Stories does not own the six-phase loop. When an acceptance scenario is still
RED after 2 consecutive fix attempts, `satisfy` / `iterate` call
`diagnostic().diagnose()` — the shared Diagnose tool (phases stay on that
tool; they are not inlined into the action markdown).

Stories-specific triggers for that call (also in the action docstrings):

- Same scenario stays RED after 2 or more consecutive fix attempts.
- Failure mode shifts (tier wiring → assertion → import) but never goes GREEN.
- RED looks like wiring or vocabulary (wrong tier import, missing Story constant, domain term drift).
- Transform / regenerate fixed the map but the leaf scenario still fails for a different surface reason.
