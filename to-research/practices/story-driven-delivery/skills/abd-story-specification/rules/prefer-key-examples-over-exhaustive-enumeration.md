# Rule: Prefer key examples over exhaustive enumeration

A specification that illustrates well with **a few key examples** is more useful than one that specifies a hundred examples poorly. List only the **key representative examples** — enough to show the pattern and catch the important boundaries. Too many examples overwhelm readers (developers cannot see the forest for the trees) and slow down test execution.

## DO

- Pick examples that **illustrate the rule**, not every permutation of it.
- Cover happy path, one or two boundaries, and the key failure — enough that the pattern is unambiguous.
- Use a **Scenario Outline** with a focused Examples table when you need breadth, rather than writing dozens of near-identical plain scenarios.

## DON'T

- Enumerate every data permutation when the underlying rule is the same — three rows that prove the formula beat thirty that restate it.
- Write exhaustive scenarios "just in case" — if you cannot articulate what a new row proves that existing rows do not, it is noise.
