# Sketch template — default terse-indent notation

Fallback template used by Sketcher when no domain-specific template is discovered. Every line is a **thing** — a class, property, operation, or concept — that has not yet earned formal naming.

## Notation

```
thing : base thing
  simple thing or thing not explored or thing defined elsewhere
  thing that has no id outside of parent
       sub thing
       sub thing
       sub operation
  thing operation thing thing        <-- should relate to things above
  associatedThing

  ----
 associatedThing
      thing
      thing operation thing
       -> _interaction_with_internal_important_enough_to_show
       -> thing.interaction_with_a_thing thing thing
```

## Legend

| Symbol | Meaning |
|---|---|
| `thing` | any concept — class, property, operation, whatever hasn't earned a distinct name yet |
| `thing : base thing` | subtype relation |
| indent | nested / owned / belongs-to |
| `----` | separator between a class block and an associated class block |
| `-> _internal_name` | interaction with an internal (private) helper |
| `-> other.operation` | interaction with another class's operation |

## Rules

- Everything is a `thing` until it earns a name. Don't over-specify.
- Indent = ownership or subordination.
- Peer classes are separated by `----`.
- Interactions are terse — `->` for both internal and cross-class.
- No headings, no tables, no keywords. Just indent + relation markers.
- Multiple `thing` on a single line implies a relation between them — resolve the exact relation during the grill loop.
- **No margin fidelity tags** (`<-i` / `<-m` / `<-s` or similar) on sketch lines. Declare fidelity once at the top if needed; do not annotate the body.
