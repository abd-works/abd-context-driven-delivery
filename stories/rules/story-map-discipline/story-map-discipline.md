---
fidelity: [shaping, discovery]
artifact: [story-map]
scanner: story-map-discipline
kind: quality

---

# Rule: Story map discipline

The story map is a **disciplined artifact**, not a wish list. Four things it must be:

1. **In scope** — every node traces to what the user asked for
2. **Evidence-based** — every node traces to a source (interview, doc, existing code, observation)
3. **Precise** — no filler, no marketing prose, no vague verbs
4. **Analysed before grouped** — nodes are grouped after evidence is collected, not before

Break any of these and the map lies. Downstream fidelities amplify the lie.

## DO

- Cite the source next to each activity or story (interview quote, doc section, code path, observation)
- Keep the map inside the scope the user requested — flag out-of-scope material as gaps, not children
- Group nodes after collecting evidence — cluster observed behaviours, don't invent categories first
- Use precise verb-noun phrases (see `verb-noun-format.md`)

## DON'T

- Add speculative "someday" activities without evidence
- Insert marketing/aspirational language ("delight the customer", "seamless experience")
- Grow the map past what the user asked for — a wider map is not a better map
- Group first and hunt for children after — the shape follows the evidence, not the other way around

## The four disciplines

### In scope

Every node is answerable with: *the user asked for this*. Track scope drift as a `## Out of scope` list, not as extra children.

```
User asked for: payment submission
In scope: activities under "Submit payment"
Out of scope (list, don't map): payment reconciliation, refunds, dispute handling
```

### Evidence-based

Every story cites its source. Formats accepted:

```
- **Customer submits payment**
  _Evidence: Interview 2026-06-14 with Ops Lead §3; existing endpoint POST /payments_
```

Or in expanded format, a `story-context.md` sitting beside the story:

```
## Source
- Interview 2026-06-14, Ops Lead §3
- POST /payments handler in src/payments/api.ts
```

If no source can be cited, either the story is speculation (drop) or the evidence collection was incomplete (go find it).

### Precise

Verb-noun format (`verb-noun-format.md`) at every level. No filler adjectives, no wrapper words.

```
Wrong — vague / marketing
- Delight the customer
- Streamline the payment experience
- Handle payment things

Correct — precise
- Submit payment
- Reject over-limit payment
- Refund settled payment
```

### Analysed before grouped

The order is: **collect evidence → cluster observed behaviours → name activities and stories → validate against source**. Not: name activities first, then reverse-engineer stories to fit.

If you find yourself asking "what stories go under this activity I just named?" — the activity was named too early.

## At each fidelity

**Shaping:** all four disciplines apply to the outcome and activity level.

**Discovery:** all four apply as stories fill in under each activity. Additionally, the scope discipline is where **gaps** get recorded — see `document-observed-quirks.md`.

## Cross-references

- `verb-noun-format.md` — precision at the naming level
- `right-size-story-nodes.md` — after evidence is collected, right-sizing is how the shape gets tuned
- `brownfield-story-mapping.md` — extra evidence rules when existing code is the source
- `document-observed-quirks.md` — how the map records what is out of scope, missing, or wrong
