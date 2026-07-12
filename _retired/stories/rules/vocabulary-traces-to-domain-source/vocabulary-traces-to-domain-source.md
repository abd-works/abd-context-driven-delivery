---
fidelity: [shaping, discovery, exploration, specification, engineering]
artifact: [story-map, thin-slice, story-scenarios, story-tests]
scanner: domain-terms-source
kind: quality

---

# Rule: Vocabulary Traces to Domain Source

Every domain term used anywhere in story artifacts — story names, epic/sub-epic
names, thin slice descriptions, AC steps, scenario steps, example table columns,
and test identifiers — must exist in a domain source artifact in the project.

## Domain sources (read in this order)

1. **Domain Specification** — typed classes with attributes and relationships (most precise)
2. **Domain Model** — concepts with responsibilities and relationships
3. **Domain Language** — glossary of agreed terms and key abstractions

## DO

- Before writing any term, look it up in domain sources
- Use the exact name the source defines — no paraphrase, no synonym
- If a term is missing from all domain sources: **stop** — list every missing term and ask how to proceed

## DON'T

- Invent terms inline without domain source backing
- Use informal shorthand when the domain has a formal name (`Contract` when source says `Payment Product Agreement`)
- Create a supplemental `domain-terms.md` file if any domain source already exists

## At each fidelity

**Shaping — epic, sub-epic, and confirming story names:**
The verb-noun in every name uses domain source vocabulary. If a name would
require inventing a term, stop and list the missing term.

**Discovery — thin slice descriptions:**
Slice names, outcomes, and any domain nouns referenced must trace to a domain
source.

**Exploration — Domain terms section:**
Every term in the story's domain terms list must exist in a domain source.
Stop and resolve before writing AC if any term is missing.

**Specification — scenario steps and table columns:**
Concept names in Given/When/Then steps and example table headers must match
domain source names exactly. Column names are snake_case of the domain term.

**Engineering — identifiers:**
Class names map to domain entities. Method names map to domain responsibilities.
Variable names in tests use snake_case of the domain term from the scenario.
