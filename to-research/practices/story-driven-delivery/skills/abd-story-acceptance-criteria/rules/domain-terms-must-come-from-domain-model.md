---
scanner: domain-terms-source
---

# Rule: Domain terms must come from the domain model

**Scanner:** `scanners/domain-terms-source-scanner.py` — `DomainTermsSourceScanner`

Every term in a story's **Domain terms** section must exist in a domain source artifact already present in the project. Domain sources include (but are not limited to):

- Domain Language (`domain-language.md`, `domain-language.md`)
- domain model (`domain-model.md`)
- Domain specification (`domain-specification.md`)
- Domain sketch (`domain-sketch.md`)
- Any file the team designates as a domain vocabulary source

## DO

- Before writing any Domain terms section, look up each term in the project's domain source files.
- Use the exact name and definition from the source. Do not paraphrase.
- If a term is missing from all domain sources, **stop — list every missing term and ask the user how to proceed** (add to Domain Language, use an existing term, skip it, etc.). Do not continue until the user decides.

## DON'T

- **NEVER create `domain-terms.md`** (or any equivalent supplement file) if any domain source file already exists in the project. If domain sources exist, they are the only source of truth. There is no bypass file.
- Invent or define terms inline without backing in a domain source.
- Silently absorb unknown terms into a new file instead of flagging them.

## `domain-terms.md` — bootstrap only, no domain sources present

`domain-terms.md` may only be created when the engagement has **no domain source files at all**. The moment any domain source exists, `domain-terms.md` must not be created. Any existing `domain-terms.md` should be merged into the real domain source and deleted.
