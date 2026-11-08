# A format's render follows the harness's render call, and the signature changes there first

Clean Engineering's and BDD's formats each write themselves with `render`, but the signatures differ: the code formats, the sketch format and BDD's models take `render(canonical, previous=None)`, the draw.io model takes `render(canonical)`, and the markdown and JSON models take `render(canonical=None)`. Round 6 (finding M17) asked for one shape, `render(previous)` on a model the practice already holds.

The shape is decided by one caller, `PracticeGuidance._call_render` in `harness/guidance/guidance.py`. It makes the target format's model, hands it the canonical model, and passes `previous` only to a `render` that names it. Every practice's formats follow that call: Stories, UX and DDD have about twenty format models that take the same arguments. Changing the signature in Clean Engineering and BDD alone would make these two practices' formats disagree with the call that drives them, which is the problem the finding names.

## Decision

Clean Engineering and BDD keep their formats' `render` as the harness's render call drives it until the call itself changes. The differences that remain are each the format's own:

- The draw.io model takes no `previous`: the diagram it keeps positions from is the Draw.io toolset's layout policy (`DrawIOCleanEngineeringModel.previous` and `keep_positioning`, set by `Drawio.create_diagram`), not the text of the target file the render call reads.
- The markdown and JSON models default `canonical` to themselves, because a model read from a document also writes itself back (`model.render()`), which the draw.io toolset and the model-document round trip use.

## Steps that close it

1. `harness/guidance` (harness core) gives the render call one shape for every practice: the practice holds the target format's model, translates the canonical model into it, and asks it to `render(previous)`.
2. Each practice's formats change to that one signature in the same change, Clean Engineering's and BDD's included; the draw.io model reads its kept diagram from `previous` and drops its own `previous` field.
3. `_call_render`'s inspection of the signature is deleted, since every format then takes the same arguments.

## Consequences

- M17 leaves the Clean Engineering and BDD count; its work is step 1, owned by harness core, and steps 2 and 3 follow in the same change.
- Until then a format that names `previous` keeps the bodies or text the target file already has, and one that does not writes from the canonical model alone.
