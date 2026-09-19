---
name: bdd
description: >-
  ## Overview
  
  Behavior-driven development turns domain vocabulary into passing tests. Every BDD artifact is an indented hierarchy. Sketch that shape first (`templates/bdd-sketch.md`).
  
  **Tooling & Idioms:** Refer to [`practices/language-tools.md`](/practices/language-tools.md) for language-specific tool recommendations and idiomatic patterns.
  
  ```
  describe {subject — domain thing, state, or observable condition}
    that {event or condition that sets the subject up}
      with {narrower condition}
        it should {observable outcome}
  ```
  
  | Line | Names | Never names |
  | --- | --- | --- |
  | **describe** | Subject under observation in plain English (thing, state, condition) | Manager / hub / runner / service / internal class; decorator symbol (`@log`); marker name |
  | **that …** | Past or present event/condition on that subject (`that has been logged`, `that is invoked`) | `when …` |
  | **with …** | Narrower standing condition (`with no session name given`, `with verbose off`) | `when …`; implementation knobs phrased as API flags |
  | **it should …** | One stakeholder-visible outcome | Internals, private fields, call counts on mocks of the subject |
  
  **Fail:**
  ```
  @log marker                          ← mechanism / symbol, not a subject
  ToolsetRunner                        ← manager / internal
  a logged tool                        ← splits the same subject; use one action story
  when no session name is given        ← never "when" for state — use "with …"
  ```
---

## Overview

Behavior-driven development turns domain vocabulary into passing tests. Every BDD artifact is an indented hierarchy. Sketch that shape first (`templates/bdd-sketch.md`).

**Tooling & Idioms:** Refer to [`practices/language-tools.md`](/practices/language-tools.md) for language-specific tool recommendations and idiomatic patterns.

```
describe {subject — domain thing, state, or observable condition}
  that {event or condition that sets the subject up}
    with {narrower condition}
      it should {observable outcome}
```

| Line | Names | Never names |
| --- | --- | --- |
| **describe** | Subject under observation in plain English (thing, state, condition) | Manager / hub / runner / service / internal class; decorator symbol (`@log`); marker name |
| **that …** | Past or present event/condition on that subject (`that has been logged`, `that is invoked`) | `when …` |
| **with …** | Narrower standing condition (`with no session name given`, `with verbose off`) | `when …`; implementation knobs phrased as API flags |
| **it should …** | One stakeholder-visible outcome | Internals, private fields, call counts on mocks of the subject |

**Fail:**
```
@log marker                          ← mechanism / symbol, not a subject
ToolsetRunner                        ← manager / internal
a logged tool                        ← splits the same subject; use one action story
when no session name is given        ← never "when" for state — use "with …"
```

behavior — Define BDD signatures — describe/it names for every observation, no test bodies.

Use MCP tool: `bdd-behavior()`

development — Implement BDD tests with production code.

Use MCP tool: `bdd-development()`
