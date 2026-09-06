---
scanner: emphasize-domain-terms
---

# Rule: Emphasize domain-significant terms

**Scanner:** `scanners/emphasize-domain-terms-scanner.py` — **`DomainTermEmphasisScanner`**

Call out **domain language** — the nouns, verbs, and short phrases that belong to the problem space and show up in stories, tests, and talk with stakeholders — so readers see what is *specific* to this product versus generic wording.

## DO

- Wrap domain-significant terms in *italics*.
- Use *title-style capitalization* inside those phrases for multi-word concepts (e.g. *Report UI*, *Export Job Progress*, *Filtered Report Rows*). Keep acronyms and product names in their normal form (e.g. *PDF*).
- Apply emphasis consistently for the same concept across AC in a story.
- Prefer this pattern over **exact** quoted UI copy unless the literal string is required for a contract or compliance check.

## DON'T

- Italicize filler or purely grammatical words, or entire sentences.
- Use emphasis as decoration on every line — only mark terms that carry domain meaning.
- Replace behavioral clarity with a wall of highlighted words; if everything is emphasized, nothing is.
