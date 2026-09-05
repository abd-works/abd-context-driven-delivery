---
scanner: emphasize-domain-terms-scenario
---

# Rule: Emphasize domain-significant terms (scenarios)

**Scanner:** `scanners/emphasize-domain-terms-scenario-scanner.py` — **`ScenarioDomainTermEmphasisScanner`**

Call out **domain language** — the nouns, verbs, and short phrases that belong to the problem space and show up in stories, tests, and talk with stakeholders — so readers see what is *specific* to this product versus generic wording. Apply this to **scenario** prose: **Background** lines, **Given / When / Then** steps, and the **scenario name** when it carries domain meaning (same bar as **abd-story-acceptance-criteria** emphasis on AC).

## DO

- Wrap domain-significant terms in *italics* in **markdown** scenario artifacts and in **story-graph** step strings when you use markdown there.
- Use *title-style capitalization* inside those phrases for multi-word concepts (e.g. *Wire Payment*, *Export Job Progress*, *Beneficiary Bank*). Keep acronyms and product names in their normal form (e.g. *PDF*).
- Apply emphasis consistently for the same concept across scenarios on a story.
- Prefer this pattern over **exact** quoted UI copy unless the literal string is required for a contract or compliance check.

## DON'T

- Italicize filler or purely grammatical words, or entire sentences.
- Use emphasis as decoration on every line — only mark terms that carry domain meaning.
- Replace behavioral clarity with a wall of highlighted words; if everything is emphasized, nothing is.
