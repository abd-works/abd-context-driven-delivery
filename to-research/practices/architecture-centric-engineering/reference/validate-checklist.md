# Architecture-Centric Engineering — Shared Validate Checklist

Apply these items during [`common/reference/rule-checklist.md`](../../../common/reference/rule-checklist.md) for every ACE practice skill.

---

## All ACE practice skills

- **No bundle markers** — `SKILL.md` has no `<!-- execute_rules:bundle_rules -->` markers.
- **Element inventory first** — no placeholder tokens (`{…}`) in element-inventory files before outline/blueprint prose.
- **Diagram verify PASS** — `.\scripts\arch-drawio.ps1 verify` prints PASS when diagrams are required.

---

## Outline

- **System context** — functions + platform tech per system; protocol per relationship.
- **Mechanisms** — all eight standard mechanisms with technology choice and NFR justification; bespoke mechanisms when context demands.
- **ADRs on disk** — mechanism and platform decisions under `docs/architecture/decisions/`.
- **No blueprint-only diagrams** at outline level.

---

## Blueprint

- **Deepens outline** — no new mechanism technology choices not in outline.
- **Four diagrams** — platform, module overview, architecture flow, testing flow — all verify PASS.
- **Mechanisms as code shapes** — prose on how modules implement each mechanism.

---

## Specification

- **Specification directory shape** — `architecture-specification.md`, `template/`, `rules/`, `scanners/` when in template mode.
- **Diagrams** — `architecture-flow.drawio` and participants diagram when required.

---

## Violations (existing systems)

- Follow [`record-all-architecture-violations.md`](../../../common/reference/record-all-architecture-violations.md) during documentation passes; deferral ADRs for deferred items.
