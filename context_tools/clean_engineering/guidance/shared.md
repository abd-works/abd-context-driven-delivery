# Clean Engineering — Procedural Guidance (shared)

## Think identity first, then structure

Before writing any class, ask: **what IS this thing?** Write one sentence that defines its unique role — what it holds, what it does, why it exists. This sentence IS the class definition. If you can't write it, the class doesn't have a clear identity yet.

This is the language pattern: prose identity precedes structural design. The sentence you write becomes the class docstring and drives every decision about what properties and operations belong on it.

## What deserves its own class

Not every noun in the domain is a class. Before promoting a concept to a class, check the three alternatives in order:

1. **Property** — does this concept just describe another thing? "remaining budget" on an Account, "active status" on a Subscription. These are properties, not classes.
2. **Instance** — is this one of a kind that already has a type? "The Gold plan" is an instance of Plan, not a separate class.
3. **Subtype** — does this specialize an existing thing? "International Payment" specializes Payment. Use inheritance, not a parallel class.

Only when none of those three fit does something deserve its own class.

## The fidelity progression

Clean Engineering deepens through three levels, each adding artifacts without inventing detail from deeper levels:

- **Modules** — thin terms, one-way dependencies, build order. Just enough to show independence.
- **Model** — empty public seam (properties and operations as stubs). The shape of the contract, not the implementation.
- **Code** — filled implementation. Everything works.

At each level, refresh the language (the prose identity) for terms already named. Don't invent method bodies at modules. Don't fill implementations at model.

## Cohesive file thinking

A class family goes in one file: the primary type, its subtypes, and tightly connected peers that only make sense together. Name the file after the family concept (`abilities.py` for `Ability` + `Abilities`).

Split into another file only when a type is independently reused across families or the file becomes a grab-bag. The default is NOT one class per file.

Exception: `{Type}ExampleFactory` always goes in a sibling file, never in the production family file.

## Naming is a design decision

Every name answers "why does this exist?" No abbreviations, no single-letter identifiers (except trivial loop indices). One word per concept across the entire model — pick one verb and use it everywhere (`fetch_`, not a mix of `fetch_`, `get_`, `retrieve_`).
