# Question: is a finished spec rendered to markdown or sketch and back meant to come back as signatures only, with its imports, setup and test bodies gone and no word about it

- **Charter:** Round 3 - BDD (behavior, realization, development) in every format: generate, render, graph
- **Tester:** Rivet
- **Story:** epic "Deliver Work With Context Guidance", sub-epic "Produce Formal Artifacts"; no scenario covers a finished spec through the tree formats.
- **Module and class:** `cdd_guidance/practices/bdd/model/bdd_model.py` `BddModel.render` (the tree holds names only), `code_spec_model.py` `CodeBddModel.render` (keeps bodies only from a `previous` file, which a render that returns content is not given).
- **Severity:** answered question

## Steps
Sandbox `C:\dev\_et\round3\rivet\work`, session `main` (`drv\run.py`, calls in `drv\trip-development.json`).

1. `_trips/development/python/src/fulfilment/shipment_spec.py`: passing Mamba spec, 2 examples, two `before.each` blocks, imports of Book, Cart, Order, Shipment.
2. `render.render {"guidance": "bdd-development", "format": "markdown", "paths": [that file], "source": "python"}` (saved beside it as `shipment_spec.md`).
3. `render.render {"guidance": "bdd-development", "format": "python", "paths": [that markdown], "source": "markdown"}`
4. The same through `sketch`, and from the Vitest specs.

## Expected
Not stated anywhere I found. Development offers python, typescript and java only, yet render takes `markdown` and `sketch` for `bdd-development` without a word. Either the trip back says the bodies are not carried, or render to a tree format is refused at development, or the bodies are kept.

## Actual
Step 3 returns

        from mamba import description, context, it
        from expects import expect

        with description("a shipment"):
            with context("that has been created for a paid order"):
                with it("should list the order's books"):
                    pass  # BDD: SIGNATURE

The tree, names and counts are kept (apart from the order change of r3-rivet-03). Imports, every `before.each` and every body are gone: body and setup lines 11 -> 2 (shipment), 13 -> 6 (cart), 15 -> 4 (order); TypeScript 14 -> 2, 16 -> 6, 17 -> 4. `isError=False` on every call. An agent that writes the returned content over the spec replaces 12 passing examples with 12 signatures.

## Tier that should catch it
Unit, once the answer is known.

## Also seen by

## Answer (2026-11-23)

A finished spec rendered to markdown or a sketch is refused, naming the tests whose bodies would be lost. Built in `cdd_guidance/practices/bdd/model/bdd_model.py` (`SpecBodiesNotKept`, `BddModel.tests_with_bodies` and `refuse_losing_bodies`, called by `BddModel.render` and `SketchBddModel.render`); at `bdd-development` and every other code fidelity, which declare no markdown, a render to markdown is refused before that by `FormatNotDeclared` (widget-16), naming the fidelity and the format. Tested by `cdd_guidance/practices/bdd/model/spec_trip_spec.py` "a finished spec taken to a tree format" and `cdd_guidance/actions/render/render_spec.py` "that is a finished Python spec, rendered to the markdown realization" and "... rendered to markdown at development, which declares none"; scenario "Refuse to render a finished spec to a format that holds no test body" in `story_tests/deliver-work-with-context-guidance/produce-formal-artifacts/produce_formal_artifacts_story.test.md`.
