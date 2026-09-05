---
scanner: scale-story-map-by-domain
---

# Rule: Scale Story Map by Domain

**Scanner:** `scanners/scale-story-map-by-domain-scanner.py` — **`ScaleStoryMapByDomainScanner`**


**Domain first, operation second.** At small scale, related domains can share a sub-epic. As behavior diverges, split into **parallel sub-epics by domain** with **consistent** stories under each. After expanding stories (*review and expand stories*), **organize by domain**, not by technology layer.

## DO

- At **small** scale, keep related domain objects together when behavior is similar and story count is low.
- As **complexity** grows, break out **by domain** with parallel structure (e.g. wire / ACH / check each with collect → validate → submit, plus domain-specific extras).
- Scale along **domain object** first; **operations** are stories **within** each domain.
- After component-level expansion, place stories under **domain** sub-epics, not under generic tech buckets.

## DON'T

- Group primarily by **operation** or **technology** at scale (e.g. one “validate all payments” mixing domains; “database operations” as a layer).
- **Over-split** early (many sub-epics for a handful of stories). **Under-specify** sub-epics as bare nouns — keep **verb–noun** flow names where they help (e.g. “Make Wire Payment” not just “Wire Transfer”).
