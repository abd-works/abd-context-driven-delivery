<!--
  Template: mechanism-tier architecture-context.md
  Use for FOLDERS THAT HOST A REUSABLE, TEMPLATED PATTERN — one that you expect
  multiple new features to extend in the same shape (e.g. Partner Integrations,
  Identity Setup, Failure Handling, Configuration & Secrets).

  PLACEMENT: this file lives in the folder it documents, NEXT TO the code it describes
  (e.g. src/integrations/architecture-context.md). It is referenced by the main spec
  using a workspace-root link like [src/integrations/](/src/integrations/architecture-context.md).

  USE WHEN: the folder defines a pattern other developers will copy. There IS a
  recipe. The recipe has a fixed skeleton + optional parts + canonical code.

  DELETE the leading "Template:" instruction block before shipping. Keep the
  section headings; remove any section that genuinely does not apply to your
  mechanism (but if you're cutting more than one, it is probably a Package, not
  a Mechanism — switch templates).
-->

---
generating-skill: abd-architecture-specification
type: mechanism
fidelity: specification
---

# Mechanism: {{MechanismName}}

### Overview

{{One short paragraph that answers: what is this mechanism for, what does it
own, and what does nothing else in the codebase own.}}

{{One short paragraph that names the composition root (or equivalent
registration point), the file skeleton each instance follows, and the role of
the central type (e.g. "the handler orchestrates the call").}}

### Why this shape

{{Crystallise the insight from the grill-me session that produced this
mechanism. Three or four short paragraphs, each with a bolded lead sentence.
Answers the question a future reader will ask: "why is it structured like this
and not the obvious naive way?"

Cover these beats — in your own words, in this order:

  1. **The problem.** What does every instance of this mechanism need to do?
     What is the naive approach and what does it cost (duplication, drift,
     forcing every extension to re-derive the same logic)?

  2. **The inversion — one or more layers.** Which thing is defined once and
     never overridden? Which specific extension points do instances contribute?
     The goal here is to name the pivot that makes the whole mechanism work.

     Many good mechanisms have MORE than one inversion, stacked. If yours
     does, name each layer separately, one paragraph per layer, each with its
     own italicised lead. Typical layering: an *algorithm* layer (one tree
     walk, template method, or lifecycle that never changes); a *structure*
     layer (each domain type owns its own shape but not the algorithm); a
     *serialization* / *transport* / *IO* layer (each backend owns only its
     own medium, nothing about structure or algorithm). Each layer sees only
     what it needs to. Making the layering explicit is what tells the reader
     which layer a new extension actually touches — and which layers it must
     not touch.

  3. **The thinking that shaped it.** Crystallise whatever came out of the
     grill-me session — the reasoning, the trade-offs weighed, the alternatives
     rejected, the constraints the team agreed to live with. This is
     free-form: it might be disciplines the mechanism enforces ("behavior
     lives in mixins, state lives in composition"; "backends never reach
     sideways"), or a trade-off that was made deliberately ("we accept N+1
     queries at load time to keep the domain layer free of caching logic"),
     or a principle that came up repeatedly ("every new instance goes through
     the composition root or it doesn't exist"). Whatever surfaced in the
     conversation and shaped the mechanism belongs here. If it took an
     argument to settle, write down what won and why — that is exactly the
     content that evaporates fastest and costs the most to rediscover.

  4. **The reference instance (optional).** If one existing instance is the
     canonical minimal example — the one a reader should learn from first —
     name it and say what it exercises. Diagrams and code backends "add a
     middle layer"; document backends "exercise the contract minimally".

This section is not decorative. When someone else later proposes an "obvious
improvement" that breaks the mechanism, this is where they discover why the
current shape exists.}}

### File Structure

```
{{folder tree showing the universal files (always present) and the optional
files (annotated "optional"). Use placeholder names like {System} or {Feature}
for the parts that vary per instance.}}
```

### Participants

{{One sentence anchoring where every file lives.}}

**{{Role}}** -- {{what it does in one sentence}}. [`{{file/path}}`](/{{file/path}})

**{{Role}}** *(optional)* -- {{what it does in one sentence; when it is present}}. [`{{file/path}}`](/{{file/path}})

{{...one paragraph per participant in the skeleton.}}

### Class Specification

```
## {{Class1Name}}  << {{Stereotype}} >>
Initialisation: {{when and how}}
------
+ {public method}({params}): {return}
    Interaction:
        {step}
        {step}
    catch (error) -> {{handler}}
----
- {private method}({params}): {return}
    Interaction:
        {step}
----

## {{Class2Name}}  << {{Stereotype}} >>  [optional]
...
```

### Rules

- **{{Rule that constrains how new instances of the mechanism are added}}** -- {{rationale or what failure looks like}}.
- **{{Rule that names what must always happen}}** -- {{...}}.
- **{{Rule that names what must never happen}}** -- {{...}}.
- {{...add as many as the mechanism needs; each rule is enforceable by reading code.}}

### Canonical Patterns

```{{language}}
// {{file in the skeleton}} -- one-line purpose
{{minimal code showing the canonical shape; uses placeholder names like
{System}, {operation}, {Domain}; readers copy + rename}}
```

{{Repeat one code block per file in the skeleton that has a non-trivial shape.}}

### Across the Codebase

{{Optional but recommended when there are multiple existing instances. Table
listing each instance and which optional parts it uses, plus any deviation from
the canonical pattern. The point is to make drift visible.}}

| Instance | {{optional1}} | {{optional2}} | Deviation |
|---|:---:|:---:|---|
| {{Name1}} | yes | - | {{what is different and why; or "none"}} |
| {{Name2}} | - | yes | {{...}} |
