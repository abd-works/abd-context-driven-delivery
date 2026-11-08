# eliminate-duplication compares operation bodies, not tables or languages

`eliminate-duplication` reports an operation whose body is the same as another's, or nearly the same (`NearCopies`: most of their three-token runs shared). It records each hit on the copying operation, which the schema now lets the graph keep. Until the round-6 fixes the schema listed the rule on classes only, so every hit it found on an operation was dropped and the rule reported nothing in a real load; a spec now checks that each rule is listed on every node type it judges.

Round 6 asked it to find two more kinds of copy: a table written twice in different shapes (the suffix-to-language table as a dict in `harness/graph/graph.py`, an if-chain in `Source.language`, and a dict in `catalog_examples.py`), and a rule written once in Python and again in TypeScript (the fidelity files' order in `fidelity-files-client.ts` and `_SUFFIX_ORDER`).

## Decision

The graph rule stays with operation bodies. The two other kinds are left to the AI validation, which reads them as concern 1 (duplicated function) and found both.

## Considered options

- **Compare module-level tables.** Rejected for now: the class models read classes and functions, not module constants, so the graph holds no table to compare; and two tables of one decision rarely share tokens when one is a dict and the other an if-chain.
- **Compare Python and TypeScript bodies.** Rejected: the two languages spell the same steps with different tokens (`for … in` against `.map(`, `None` against `null`), so a token measure either misses the pair or matches unrelated code that happens to share names.

## Consequences

- A table or a rule duplicated across shapes or languages is found by reading, not by the graph. The validators' checklist for `*-client.ts` and `App.tsx` (any `filter`, `sort`, or constant table over domain words) covers the TypeScript side.
- The graph rule does find copy-and-adjust copies of an operation inside one language, and now reports them.
