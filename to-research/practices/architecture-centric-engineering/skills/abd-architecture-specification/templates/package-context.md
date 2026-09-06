<!--
  Template: package-tier architecture-context.md
  Use for FOLDERS WITH ENOUGH FUNCTIONALITY to warrant their own page but
  WITHOUT a templated pattern that new features extend.

  PLACEMENT: lives in the folder it documents (e.g. src/adapters/SupportTickets/
  architecture-context.md). Referenced by the main spec using a workspace-root
  link.

  USE WHEN: the folder is an adapter, third-party SDK wrapper, or functional
  subsystem with meaningful surface area (multiple public operations, non-trivial
  behaviour, specific consumers). There is NO copy-the-skeleton recipe for new
  instances — there is at most one of these.

  USE A DIFFERENT TEMPLATE WHEN:
   - There is a reusable recipe new code follows → mechanism-context.md
   - The folder is small or a grab-bag of unrelated utilities → miscellaneous-context.md

  STOP BEFORE drifting into domain documentation. Describe what the package does,
  how it works at the seams, and who uses it. If you find yourself documenting
  business rules or domain invariants, that belongs in the domain spec, not here.

  DELETE the leading "Template:" instruction block before shipping. Drop any
  section that is genuinely empty for your package.
-->

---
generating-skill: abd-architecture-specification
type: package
fidelity: specification
---

{{One opening paragraph: what this package is, who uses it, and what
distinguishes it from the rest of the system. If usage is exclusive to a single
consumer (e.g. "used exclusively by the PartnerA integration handler"), say so
here.}}

{{Optional second paragraph: anything that affects how you should think about
it — for example: it wraps a third-party SDK, it predates the current pattern,
it is the only path for X, it bypasses Y.}}

---

{{If the package exposes a meaningful API surface — payload builders, public
methods, named operations — list them with a one-line "when this is called"
description. Bold the name, keep the description to one sentence, prefer
present tense.}}

**`{{methodOrSymbol}}`** -- {{when and why this is called; what it produces}}.

**`{{methodOrSymbol}}`** -- {{...}}.

**`{{methodOrSymbol}}`** -- {{...}}.

{{...one bold-name paragraph per public method or symbol that matters. Group
related variants on the same line (e.g. `defaultPayload('id')` /
`defaultPayload('pSim')`) when they only differ by a discriminator.}}
