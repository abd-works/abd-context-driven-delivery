---
rule: category-headings-not-subjects
severity: error
---
# Category Headings Are Markdown, Not Describes

Organizational scaffolding — the labels that group subjects into sections like *Story Model*, *Documents*, *Diagrams*, *Code* — is markdown structure. Use `##` headings. Never use a bare category label as a top-level describe. Every top-level describe must be a domain-concept subject that could stand on its own if lifted out of the file.

The test is simple: read the top-level describe alone, without the file that contains it. If it names a *thing whose state you can observe*, it is a valid subject. If it names a *category of things*, it is a heading in disguise.

## Why this matters

A describe is a state carrier. Every nested describe below it narrows the state; every leaf observes something about that state. A category label like `Diagrams` names no state. Nothing can be true or false of `Diagrams` in the way something can be true of `a diagram Story Map with 4 Epics`. When you push a category label to the top of the tree, the whole hierarchy below it inherits a phantom parent that has no state to narrow, so the observations start floating and the reader loses the thread.

Marking categories as markdown headings and starting each section with a real subject preserves both the reader's navigation and the state-carrying integrity of every describe below.

## Test — does the top-level describe stand on its own?

Isolate any top-level describe from its surrounding file. If it still names an observable thing, it is a subject. If it only makes sense as an organizing label, it is a heading.

| Line | Stands alone? | Verdict |
|---|---|---|
| `a Story Map` | yes — an instance whose state you can observe | subject ✓ |
| `a Markdown document` | yes — a document whose contents you can observe | subject ✓ |
| `a diagram Story Map` | yes — a Story Map rendered as a diagram, observable | subject ✓ |
| `a code Story Map` | yes — a Story Map rendered as code, observable | subject ✓ |
| `Story Model` | no — a category of things | heading ✗ |
| `Documents` | no — a category of things | heading ✗ |
| `Diagrams` | no — a category of things | heading ✗ |
| `Code` | no — a category of things | heading ✗ |

## DO

Categories as `##` markdown headings; each section begins with a real subject:

```
## Story Model

a Story Map
  it should hold no Epics
  with 4 Epics in sequential order
    …

## Documents

a Markdown document
  that holds a rendered Story Map with 4 Epics …
    …

a JSON document
  that holds a rendered Story Map with 4 Epics …
    …

## Diagrams

a diagram Story Map
  that holds a rendered Story Map with 4 Epics …
    …

a DrawIO Story Map
  <!-- Only DrawIO-specific proofs live here. -->
  …

## Code

a code Story Map
  that holds a rendered Story Map with 4 Epics …
    …

a TypeScript story-spec Story Map
  <!-- Only TypeScript-specific proofs live here. -->
  …
```

## DO NOT

Bare category labels as top-level describes:

```
Story Model

  a Story Map
    …

Documents

  a Markdown document
    …

Diagrams

  a DrawIO Story Map
    …

Code

  a code Story Map
    …
```

The categories `Story Model`, `Documents`, `Diagrams`, `Code` name nothing observable. They should be `##` markdown headings, not describes.

## Interaction with abstract-subject-then-concrete-backends

The `abstract-subject-then-concrete-backends` pattern lives inside a category section. The category is the `##` heading. The abstract subject is the first top-level describe under the heading. The concrete backends are the top-level describes that follow, each thin and each explicitly deferring to the abstract subject.

```
## Diagrams              ← markdown heading (organizational)

a diagram Story Map      ← abstract domain subject (shared behavior)
  …

a DrawIO Story Map       ← concrete backend (thin)
  …

a Miro Story Map         ← concrete backend (thin)
  …
```
