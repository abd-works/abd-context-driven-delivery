---
rule: abstract-subject-then-concrete-backends
severity: error
---
# Abstract Subject Then Concrete Backends

When a domain has multiple concrete backends that share the same behavior but differ in serialization, storage medium, or rendering, model the shared behavior once on an **abstract domain subject**. Each concrete backend then adds only what is genuinely different — the serialization proofs, the on-disk shape, the parse/typecheck fact. Concrete backends **never restate** the structural, hierarchical, or reconciliation behavior that already lives on the abstract subject.

The abstract subject is a real domain concept, not a class name. It carries every observation that would be true regardless of the backend chosen. Concrete backend subjects are thin — often only a handful of describes — and every observation is something the abstract subject cannot state without picking a backend.

## When to apply

You need this pattern when two or more concrete backends produce different artifacts from the same story-map operations. Examples in this repo:

- A Story Map rendered to a diagram — DrawIO and Miro both draw the same nodes at the same rows; only the underlying element shape (mxCell XML vs Miro shape payload) differs.
- A Story Map rendered to code — TypeScript spec-data files, Python pytest classes, and Java JUnit classes all follow the same `Epic → folder → sub-epic → leaf file → Story block → Scenario` shape; only the leaf-file syntax differs.

If you catch yourself writing the same `with a fifth Epic appended → the folder for the Epic → it should …` observation under three different backend subjects, you have missed this pattern.

## How to structure it

1. Introduce the abstract subject first — `a diagram Story Map`, `a code Story Map`. Give it every state elaboration and every observation that describes the shared behavior in the domain vocabulary of the domain (Epic, SubEpic, Story, folder, row, block).
2. Introduce each concrete backend subject afterwards — `a DrawIO Story Map`, `a Miro Story Map`, `a TypeScript story-spec Story Map`, `a Python acceptance-test Story Map`, `a Java acceptance-test Story Map`. Immediately below the subject, write one comment that says: *every behavior on the abstract subject applies; only the backend-specific artifact proofs live here*.
3. Under each concrete backend, only add observations that would be nonsense on the abstract subject — filename patterns, syntactic tokens (`export const`, `class Test<Story>`, `@Nested`), parse/compile facts, payload deltas.

## The one-word test

Read a concrete backend describe out loud. If you can replace the backend name with any other backend name and the observation still makes sense, it belongs on the abstract subject, not here.

- ✓ `a DrawIO Story Map → every mxCell for an Epic → it should sit on the Epic row at y = 0` — nonsense as a Miro observation, correct placement.
- ✗ `a DrawIO Story Map → with a fifth Epic appended → it should hold 5 Epic cells on the Epic row` — the "5 Epic cells" fact is really "the diagram now has 5 Epic elements", which is the abstract `a diagram Story Map` behavior expressed via the shared `diagram Story Map` vocabulary. Move it up.

## DO

```
a diagram Story Map
  that holds a rendered Story Map with 4 Epics
    it should contain 4 Epic elements on the Epic row
    with a fifth Epic appended
      it should contain 5 Epic elements on the Epic row

a DrawIO Story Map
  <!-- Every "a diagram Story Map" behavior applies. Only DrawIO-specific
       serialization proofs live here. -->
  that holds a rendered diagram Story Map with 4 Epics
    every Epic element
      it should be an mxCell whose style carries the Epic swatch
    the serialized diagram
      it should parse as valid draw.io XML

a Miro Story Map
  <!-- Every "a diagram Story Map" behavior applies. Only Miro-specific
       payload proofs live here. -->
  that holds a rendered diagram Story Map with 4 Epics
    every Epic element
      it should be a Miro shape with the Epic style token
    the serialized diagram
      it should be an array of Miro-API payload objects
```

## DO NOT

Restate structural or reconciliation behavior under a concrete backend:

```
a DrawIO Story Map
  that holds a rendered Story Map with 4 Epics
    it should contain 4 Epic elements on the Epic row  ← already on the abstract subject
    with a fifth Epic appended
      it should contain 5 Epic elements                 ← already on the abstract subject
      the first 4 Epic elements
        it should be unchanged                          ← already on the abstract subject

a Miro Story Map
  that holds a rendered Story Map with 4 Epics
    it should contain 4 Epic elements on the Epic row  ← duplicated verbatim
    with a fifth Epic appended
      it should contain 5 Epic elements                 ← duplicated verbatim
```

Or introduce a concrete backend without an abstract subject when you have two or more concrete backends sharing behavior:

```
<!-- No `a diagram Story Map` subject, so structural behavior must be
     repeated per backend. Do not do this. -->

a DrawIO Story Map
  with a fifth Epic appended
    it should contain 5 Epic elements
    …every structural observation duplicated…

a Miro Story Map
  with a fifth Epic appended
    it should contain 5 Epic elements
    …every structural observation duplicated…
```

## Why this matters

Concrete backends will grow. Every duplicated observation is a place where the backends silently drift out of alignment. Modelling the shared behavior once on the domain subject and keeping the concrete subjects thin makes the specification survive new backends being added and old ones being replaced.
