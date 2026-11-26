# A spec rendered from Python to TypeScript and back (or the other way) comes back with every test body and setup commented out under "typescript body to translate: // python body to translate:", and each further trip wraps them again

- **Charter:** Round 3 - BDD (behavior, realization, development) in every format: generate, render, graph
- **Tester:** Rivet
- **Story:** epic "Deliver Work With Context Guidance", sub-epic "Produce Formal Artifacts"; no scenario covers a spec with bodies between two languages.
- **Module and class:** `cdd_guidance/practices/bdd/model/code_spec_model.py` `CodeBddModel._render_body` / `_render_inside` / `_foreign`, and `cdd_guidance/practices/clean_engineering/model/code_body.py` `CodeBody.in_language_of` / `lines_in` (a body of the other language is written as comments under "<language> body to translate:"; read back, that comment block is a body of this language, so the original is not recognised).
- **Severity:** wrong result

## Steps
Sandbox `C:\dev\_et\round3\rivet\work`, session `main` (`drv\run.py`, calls in `drv\trip-development.json` and `drv\trip-realization.json`).

1. `_trips/development/python/src/ordering/order_spec.py`: the passing Mamba spec (4 examples, `before.each` in the describe and in three states).
2. `render.render {"guidance": "bdd-development", "format": "typescript", "paths": [that file], "source": "python"}`, save as `order.spec.ts`.
3. `render.render {"guidance": "bdd-development", "format": "python", "paths": [that order.spec.ts], "source": "typescript"}`
4. The same starting from the Vitest spec, and at `bdd-realization` with specs whose bodies are call-graph comments only.

## Expected
Back in its own language the spec is what it was (charter check 2: "and back, without losing or changing what it holds"). At realization, where a body is only `# ->` comment lines, the other language holds the same lines as its own comments (`// ->`).

## Actual
Step 2: the tree is kept; each body and setup is a comment block, and each `it` holds `// BDD: SIGNATURE`, so a finished spec reads as unfinished:

        it("should be paid", () => {
          // python body to translate:
          // expect(self.order.is_paid).to(be_true)
          // BDD: SIGNATURE
        });

Step 3:

        with it("should hold a line for each cart line"):
            # typescript body to translate:
            # // python body to translate:
            # // expect(self.order.lines).to(have_length(2))
            # // BDD: SIGNATURE
            pass  # BDD: SIGNATURE

The imports of `Book`, `Cart`, `Order` are replaced by `from mamba import description, context, it` / `from expects import expect`; every `before.each` is a comment; 12 passing examples become 12 signatures. Body lines grow on each trip (order spec 15 -> 39, cart 13 -> 43).

At realization the call graph comes out as

        // python body to translate:
        // # order.status
        // #   <- str
        // pass  # BDD: SIGNATURE
        // BDD: SIGNATURE

with the marker twice, and nests the same way on the way back.

At behavior the trip is clean both ways, apart from `from expects import expect` added to a Python spec that did not import it.

## Tier that should catch it
Unit: `code_spec_render_spec.py` checks one direction; no example goes to the other language and back.

## Also seen by
Widget, round 2 notes ("bdd python -> typescript keeps the tree, bodies as comments 'python body to translate'"), not reported then.
