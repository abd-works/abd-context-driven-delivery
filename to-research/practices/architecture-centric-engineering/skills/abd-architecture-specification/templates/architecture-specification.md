<!--
  Template: architecture-specification.md (the main spec document).
  STACK-AGNOSTIC.

  THIS DOCUMENT IS A SHORT NAVIGATION HUB, NOT A KITCHEN-SINK.
  The detail lives in per-folder architecture-context.md files alongside the
  code. This document's job is to:
    1. Route a developer to the right context files via "Where to Start"
    2. Name every mechanism in one line + link
    3. List every documented package + link (Package Context)
    4. Show the folder tree with which mechanism/package each folder implements
    5. Note any per-instance variation in how the domain is realised
    6. Point to the testing context file

  PLACEMENT: docs/architecture/specification/architecture-specification.md.

  LINK CONVENTION: all internal links use workspace-root paths starting with `/`
  (e.g. `/src/adapters/OutboundClient/architecture-context.md`). NEVER wrap a link in
  backticks — it will render as code and won't be clickable.

  THREE TIERS OF CONTEXT FILES the main spec links into:
    - mechanism  (templated pattern)   → templates/mechanism-context.md
    - package    (functional area)     → templates/package-context.md
    - misc       (tiny or grab-bag)    → templates/miscellaneous-context.md

  DELETE this instruction block before shipping.
-->

# {{ProjectName}} Architecture Specification

> **Status:** Draft -- {{Exploration | Specification}} fidelity
> **Date:** {{YYYY-MM-DD}}
> **Mode:** {{document | template}}

---

## Where to Start -- What Does This Feature Touch?

<!--
  Entry point. Frame each question around a REQUIREMENT the feature has, not
  the technical change it would cause. The reader answers yes/no and follows
  the link for any "yes". They never have to read the rest of this document.

  EXAMPLES OF GOOD QUESTIONS (requirements-framed):
    - "Is there a new downstream system to integrate with?"
    - "Does it require a new third-party credential or environment-specific value?"
    - "Should access be restricted to authenticated or specific users?"
    - "Are there specific failure conditions the caller needs to distinguish?"
    - "Does it involve number portability or SMS verification?"

  EXAMPLES OF BAD QUESTIONS (technical-framed — DO NOT USE):
    - "Does it add a new entry point?"   (entry point is the technical effect, not the need)
    - "Does it need a new config key?"  (config key is the implementation)
    - "Does it return a new error shape?" (asks about code, not requirement)

  COVERAGE: every mechanism in the spec MUST appear as the target of at least
  one row. Services/packages that are likely to be touched by feature work
  (e.g. Twilio, Zendesk) SHOULD appear too. Pure infrastructure that no story
  ever extends does not need a row.
-->

Answer each question about the feature or story you are working on. Each "yes"
points to a context file with the details you need. Read only those files --
you don't need the rest of this document.

| Question                                                                  | Read this                                                       |
| ------------------------------------------------------------------------- | --------------------------------------------------------------- |
| {{Requirement question 1}}                                                 | [{{Package1}}](/{{path}}/architecture-context.md)              |
| {{Requirement question 2}}                                                 | [{{Package2}}](/{{path}}/architecture-context.md)              |
| {{Requirement question 3}}                                                 | [{{Package3}}](/{{path}}/architecture-context.md)              |
| {{Requirement question 4}}                                                 | [{{Package4}}](/{{path}}/architecture-context.md)              |

---

## Overview

{{One short paragraph: what this system is, who it sits between, what it does
NOT do (state ownership, business rules, etc.), and how a request flows
through it at the highest level. No principle list — keep it human.}}

{{Optional second paragraph naming the small set of concerns the architecture
has — typically 3 to 5 — in one sentence.}}

> **Sources:** {{ADRs, blueprint doc, sibling-skill output that the spec is
> grounded in}}.

---

## Mechanisms

<!--
  ONE LINE PER MECHANISM in this section. Each line: bold name, folder path,
  one-sentence description, link to its mechanism-tier architecture-context.md.
  DO NOT inline file structures, participant tables, or sequence diagrams here.
  All of that lives in the linked context file.

  A mechanism is a REUSABLE TEMPLATED PATTERN that new features extend in the
  same shape. If it isn't templated, it's a package — list it under Package
  Context instead.
-->

**{{Mechanism1Name}}** (`{{folder}}/`) -- {{one-sentence what+how}}. [{{path}}](/{{path}}/architecture-context.md)

**{{Mechanism2Name}}** (`{{folder}}/`) -- {{one-sentence what+how}}. [{{path}}](/{{path}}/architecture-context.md)

**{{Mechanism3Name}}** (`{{folder}}/`) -- {{one-sentence what+how}}. [{{path}}](/{{path}}/architecture-context.md)

**{{Mechanism4Name}}** (`{{folder}}/`) -- {{one-sentence what+how}}. [{{path}}](/{{path}}/architecture-context.md)

### Package Context

<!--
  Every folder with significant logic that has an architecture-context.md
  alongside it MUST appear here. Group by category. One bullet each: bold
  name, one-sentence description, link to the context file.

  Standard categories (drop a category if empty; rename if needed):
    - Mechanisms     (re-list every mechanism above with its context link)
    - Services       (packages — third-party SDKs, infrastructure singletons)
    - Utilities & Legacy   (miscellaneous / grab-bag / dead code)
    - Testing        (test helpers / domain test objects)
-->

Every folder with significant logic has an `architecture-context.md` alongside
its code.

**Mechanisms**

- **{{Mechanism1Name}}** -- {{one-liner}} [{{path}}/](/{{path}}/architecture-context.md)
- **{{Mechanism2Name}}** -- {{one-liner}} [{{path}}/](/{{path}}/architecture-context.md)
- **{{Mechanism3Name}}** -- {{one-liner}} [{{path}}/](/{{path}}/architecture-context.md)

**Services**

- **{{Service1}}** -- {{one-liner; note "used by X only" if relevant}} [{{path}}/](/{{path}}/architecture-context.md)
- **{{Service2}}** -- {{one-liner}} [{{path}}/](/{{path}}/architecture-context.md)

**Utilities & Legacy**

- **{{Misc1}}** -- {{one-liner; flag legacy/dead code here}} [{{path}}/](/{{path}}/architecture-context.md)
- **{{Misc2}}** -- {{one-liner}} [{{path}}/](/{{path}}/architecture-context.md)

**Testing**

- **{{TestHelpers}}** -- {{one-liner}} [{{path}}/](/{{path}}/architecture-context.md)

### Source Layout

<!--
  Annotated tree. EVERY folder shown carries a bracketed tag pointing to the
  mechanism or package it implements, OR an explicit tag like [dead code] /
  [legacy] for inactive folders. Miscellaneous-tier folders (e.g. logging)
  still get a bracketed tag matching their Package Context name.
-->

```
{{rootFolder}}/
+-- {{entry}}.{{ext}}      <- {{role}}                          [{{Mechanism}}]
+-- {{root}}.{{ext}}       <- composition root
+-- {{folder1}}/           <- {{role}}                          [{{Mechanism}}]
+-- {{folder2}}/           <- {{role}}                          [{{Mechanism}}]
+-- {{utilFolder}}/        <- {{description}}
|   +-- {{sub1}}/          <- {{role}}                          [{{Mechanism}}]
+-- {{servicesFolder}}/
|   +-- {{svc1}}/          <- {{role}}                          [{{Package}}]
|   +-- {{svc2}}/          <- {{role}}                          [{{Mechanism}}]
|   +-- {{svc3}}/          <- {{role}}                          [{{Package}}]
+-- {{deadFolder}}/        <- {{description}}                   [dead code]
```

### Instantiating the Domain

<!--
  Optional but recommended when entity / module realisations vary. The point
  is to flag WHERE THE PATTERN IS NOT UNIFORM, so a developer doesn't try to
  copy the wrong example.

  KEEP IT TO A SHORT BULLETED OBSERVATION LIST. Do NOT turn this into a full
  domain-mapping section with diagrams — that drifts into the domain spec.
-->

> **{{One-sentence headline observation}}** — e.g. "Entity implementation
> patterns vary significantly. Folders are named after the external system,
> not domain concepts (ADR-XXX)."
>
> - **{{InstanceA}}** -- {{how it instantiates the domain}}.
> - **{{InstanceB}}** -- {{how it instantiates the domain}}.
> - **{{InstanceC}}** -- {{...}}.

---

## Testing Architecture

<!--
  ONE PARAGRAPH only. Name the testing pattern and the stub boundary. Point
  the reader to tests/<helpers>/architecture-context.md for everything else —
  test object structure, fixture layout, epic/sub-epic map, spec-alignment
  table. NEVER inline that material here.
-->

Tests use a **{{Pattern}}** pattern: {{one sentence on what drives the tests,
what runs for real, and what is stubbed at the boundary}}. See
[{{path}}](/{{path}}/architecture-context.md) for principles, file layout,
{{any other detail kept in the context file}}.

---

## References

- **Architecture source of truth:** {{ADR / blueprint / wiki}}
- **Decision records:** {{ADR-001 .. ADR-N or path to ADR folder}}
- **Domain model:** {{domain spec / model paths}}
- **Acceptance criteria:** {{stories / acceptance-criteria paths}}
- **Coding standard:** {{e.g. abd-clean-code or project guide}}
- **Testing standard:** {{e.g. abd-story-acceptance-test}}
