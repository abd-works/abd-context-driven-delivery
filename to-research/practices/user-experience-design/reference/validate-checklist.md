# User Experience Design — Shared Validate Checklist

Apply these items during [`common/reference/rule-checklist.md`](../../../common/reference/rule-checklist.md) for every UX practice skill.

---

## All UX practice skills

- **No bundle markers** — `SKILL.md` has no `<!-- execute_rules:bundle_rules -->` markers.
- **Template instructions omitted** — generated project files contain stakeholder-facing content only.
- **Verbatim upstream** — story names, domain terms, and AC clauses copied character-for-character where rules require.

---

## Impact map

- **Cross-artifact parity** — hierarchy, ASCII, and hypotheses file pairs align on goals, actors, impacts, deliverables.
- **Behavioural impacts** — impacts are observable behaviour changes, not team tasks.

---

## Information architecture

- **Diagram on disk** — `initial-ia.drawio` exists with Detailed IA and Site Map pages.
- **ARIA files** — `docs/ux/ia/<screen-slug>.aria.yaml` per in-scope screen at structural fidelity.
- **Cross-artifact parity** — `initial-ia.md` and diagram describe the same screens and transitions.

---

## Mockup

- **Diagram on disk** — `<screen-slug>.drawio` per screen before cell done.
- **State sync** — `<screen-slug>-state.json` and `.drawio` in sync.
- **ARIA detailed** — `docs/ux/mockups/<screen-slug>.aria.yaml` at detailed fidelity.

---

## Specification

- **Clicks work** — primary flows navigable without developer explanation.
- **Stub catalogue** — `ux-specification.md` lists what is faked; no silent pretence of production services.
- **AC demonstration map** — every AC has a documented click path or explicit gap.
