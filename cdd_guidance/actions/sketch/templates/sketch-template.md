# Sketch template — default heading-and-indent notation

Fallback template used by Sketch when no domain-specific template is discovered. Every line is a **thing** — a class, property, operation, or concept — that has not yet earned formal naming.

## Notation — headings carry the hierarchy

Each level of the tree is a markdown heading, so every branch folds on its own. The practice section is the `##` heading; the tree starts one level below it. Detail that has not earned a heading sits in a fenced block under the heading that owns it.

| Heading | Holds |
|---|---|
| `### {thing}` | a top-level thing |
| `#### {thing}` | a thing owned by the one above |
| `##### {thing}` | and so on, as deep as the shape needs |

---

## Template

~~~markdown
### {thing} : {base thing}

```
simple thing or thing not explored or thing defined elsewhere
thing that has no id outside of parent
     sub thing
     sub operation
thing operation thing thing        <-- should relate to things above
associatedThing
```

### {associatedThing}

```
thing
thing operation thing
  -> _interaction_with_internal_important_enough_to_show
  -> thing.interaction_with_a_thing thing thing
```
~~~

## Legend

| Symbol | Meaning |
|---|---|
| `thing` | any concept — class, property, operation, whatever hasn't earned a distinct name yet |
| `thing : base thing` | subtype relation |
| heading depth | nested / owned / belongs-to |
| indent inside a fence | nested / owned / belongs-to, below the heading's thing |
| `-> _internal_name` | interaction with an internal (private) helper |
| `-> other.operation` | interaction with another class's operation |

## Rules

- Everything is a `thing` until it earns a name. Don't over-specify.
- A heading owns everything under it, until the next heading at the same depth or shallower.
- Peer things are peer headings — one per thing, not a `----` separator.
- Interactions are terse — `->` for both internal and cross-class.
- No tables, no keywords inside the fence. Just indent + relation markers.
- Multiple `thing` on a single line implies a relation between them — resolve the exact relation during the grill loop.
- **No margin fidelity tags** (`<-i` / `<-m` / `<-s` or similar) on sketch lines. Declare fidelity once at the top if needed; do not annotate the body.
