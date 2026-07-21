# CDR Format (Context Decision Record)

CDRs live in `.context/cdr/` and use sequential numbering: `0001-slug.md`, `0002-slug.md`, etc.

Create the `.context/cdr/` directory lazily — only when the first CDR is needed.

## Template

```md
# {Short title of the decision}

{1-3 sentences: what's the context, what did we decide, and why.}
```

That's it. A CDR can be a single paragraph. The value is in recording *that* a decision was made and *why* — not in filling out sections.

## Optional sections

Only include these when they add genuine value. Most CDRs won't need them.

- **Status** frontmatter (`proposed | accepted | deprecated | superseded by CDR-NNNN`) — useful when decisions are revisited
- **Considered Options** — only when the rejected alternatives are worth remembering
- **Consequences** — only when non-obvious downstream effects need to be called out

## Numbering

Scan `.context/cdr/` for the highest existing number and increment by one.

## When to offer a CDR

All three of these must be true:

1. **Hard to reverse** — the cost of changing your mind later is meaningful
2. **Surprising without context** — a future reader will look at the artifact and wonder "why on earth did they do it this way?"
3. **The result of a real trade-off** — there were genuine alternatives and you picked one for specific reasons

If a decision is easy to reverse, skip it — you'll just reverse it. If it's not surprising, nobody will wonder why. If there was no real alternative, there's nothing to record beyond "we did the obvious thing."

### What qualifies

- **Structural shape.** Module boundaries, fidelity choices, generator partitioning.
- **Integration patterns between contexts.** How concepts compose or hand off.
- **Technology choices that carry lock-in.** Not every library — just the ones that would take meaningful effort to swap out.
- **Boundary and scope decisions.** What is in vs out of a context; the explicit no-s are as valuable as the yes-s.
- **Deliberate deviations from the obvious path.** Anything where a reasonable reader would assume the opposite.
- **Constraints not visible in the artifacts.** Compliance, partner contracts, non-negotiable timing.
- **Rejected alternatives when the rejection is non-obvious.** Otherwise someone will suggest the rejected option again later.
