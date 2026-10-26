---
description: "Use these rules whenever you name a concept, draw a dependency, or write a public seam — in prose, a diagram, or source."
paths:
  - "**/*-sketch.md"
---

## Shared rules



Use these rules whenever you name a concept, draw a dependency, or write a public seam — in prose, a diagram, or source.

- **`vocabulary-traces-to-source`** — Take every term from the source. The English term and the code name are the same word: *shopping cart* is `ShoppingCart`. When the code says a different word than the domain, every reader keeps a translation in their head, and the two names drift until they mean different things.
- **`do-not-invent-terms`** — Do not invent a second noun or a parallel vocabulary. A second noun for the same thing becomes a second class, and then the same rule has to be written and fixed in both.
- **`do-not-invent-parallel-object-models`** — Keep one object model. Follow the nouns and verbs the rest of the graph already uses for that concept. A class that joins types the rest of the graph keeps apart is a second model — a big ball of mud — and every rule then has to be written and fixed in both. Wrap or extend the live objects and name a wrapper after the type it represents; do not scrape the same data into a second `*Model` or `*Entry` family.

---