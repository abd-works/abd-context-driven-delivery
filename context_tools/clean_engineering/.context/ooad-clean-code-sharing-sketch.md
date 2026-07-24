# Sketch — clean_engineering + CleanCode Integration (v4 — FINAL)

## The design

Engineering is the 4th fidelity of OOAD. ooad.md Concepts is the shared base
loaded by every fidelity. No extra folders, no inheritance chains.

```
clean_engineering fidelity axis
  language       prose — named concepts, responsibilities, collaborations
  model          class shells, operations shelled, relationships decided
  specification  type-safe, fully shelled, invariants, cardinality
  engineering    all implementations completed — clean code discipline applied
```

## Shared base — ooad.md Concepts

ooad.md Concepts is read by every fidelity.
It already owns:
  what is a class (identity, state, behavior, structure, interactions)
  responsibilities (hold / do / both)
  properties (noun phrase, typed, encapsulates information)
  operations (verb phrase, stateless or stateful, has parameters + return)
  relationships (composition / aggregation / association, direction)
  inheritance and subtypes (base class, delta only, Liskov)
  class design rules
    keep-classes-single-responsibility
    hide-inner-details
    eliminate-duplication
    use-explicit-dependencies

Fidelity guides add only what is specific to them. No duplication.

## File changes

```
context_tools/clean_engineering/ooad.py
  _VALID_FIDELITIES  add "engineering"
  _FIDELITY_FORMAT_DEFAULTS  "engineering": "python"

context_tools/clean_engineering/fidelities/engineering/     (new)
  domain-generate.md             <- engineering guide: adds operation discipline,
                                    naming, error handling, comments, full impl bodies
  rules/                         <- engineering-specific rules (renamed from clean_code)
  examples/                      <- from clean_code/formats/

clean_code/clean_code.py         <- becomes thin alias
  class CleanCode(clean_engineering):
      def __init__(self, format=None):
          super().__init__(fidelity="engineering", format=format)

clean_code/clean-code.md         <- content migrates to context_tools/clean_engineering/fidelities/engineering/
                                    class design section drops (already in Concepts)
```

## Vocabulary fix in engineering guide

"Function" -> "Operation" throughout.
Section: "Operation discipline" (was "Function discipline")
Rules:
  keep-operations-single-responsibility
  keep-operations-small-focused
  use-clear-operation-parameters
  (separate-concerns, simplify-control-flow, maintain-abstraction-levels — unchanged)

## What stays in clean_code/

clean_code.py  — thin alias (CleanCode = clean_engineering at engineering fidelity)
formats/       — language-specific scanners stay here; they test generated code

## What moves to context_tools/clean_engineering/

clean-code.md content -> context_tools/clean_engineering/fidelities/engineering/domain-generate.md
  minus: class design section (already in ooad.md Concepts)
  plus:  "operation" vocabulary throughout

## DDD follows the same pattern

When DDD is wired: it too loads ooad.md Concepts as shared base,
adds domain-specific layer (ubiquitous language, bounded context, aggregates).
Same pattern, no special mechanism needed.
