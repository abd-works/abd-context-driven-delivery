"""BDD spec — a sketch whose hierarchy is carried by markdown headings."""

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import equal, expect
from mamba import before, description, it

from harness.sketch.sketch_outline import SketchLens, SketchOutline

_HEADED = """# Single Client View — sketch

fidelity: discovery

---

## stories:

### Unify Client Identity

#### Resolve Client

##### Call Centre --> Resolve Client From Record In Hand

###### client resolved from the record in hand

```
given a Client Identity in hand
when the Call Centre opens the view
then the Client is shown
```

## domain driven design:

### Single Client View | custom

#### Client

##### Client

```
emits events:
  - ClientMatched
members:
  - Client Identity
```
"""

_FLAT = "shop/\n  Cart\n    total\n"


with description("a sketch that carries its hierarchy in markdown headings"):
    with before.each:
        self.outline = SketchOutline(_HEADED, 4)

    with it("should name the practices it holds a section for"):
        expect(
            [
                self.outline.holds(SketchLens.stories),
                self.outline.holds(SketchLens.domain_driven_design),
                self.outline.holds(SketchLens.user_experience),
            ]
        ).to(equal([True, True, False]))

    with description("that is read for one practice"):
        with it("should nest each heading one level deeper than the heading above it"):
            expect(self.outline.body_for(SketchLens.stories)).to(
                equal(
                    "\n"
                    "Unify Client Identity\n"
                    "\n"
                    "    Resolve Client\n"
                    "\n"
                    "        Call Centre --> Resolve Client From Record In Hand\n"
                    "\n"
                    "            client resolved from the record in hand\n"
                    "\n"
                    "                given a Client Identity in hand\n"
                    "                when the Call Centre opens the view\n"
                    "                then the Client is shown\n"
                    "\n"
                )
            )

        with it("should leave the other practice's section out"):
            expect("ClientMatched" in self.outline.body_for(SketchLens.stories)).to(
                equal(False)
            )

        with it("should nest at the width that practice's notation uses"):
            expect(
                SketchOutline(_HEADED, 2).body_for(SketchLens.domain_driven_design)
            ).to(
                equal(
                    "\n"
                    "Single Client View | custom\n"
                    "\n"
                    "  Client\n"
                    "\n"
                    "    Client\n"
                    "\n"
                    "      emits events:\n"
                    "        - ClientMatched\n"
                    "      members:\n"
                    "        - Client Identity\n"
                )
            )

    with description("that names a lens the sketch does not hold"):
        with it("should read as an empty section"):
            expect(self.outline.body_for(SketchLens.behavior_driven_development)).to(
                equal("")
            )


with description("a sketch that names no lens"):
    with it("should read as one section of indented lines"):
        expect(SketchOutline(_FLAT, 2).body_for(SketchLens.clean_engineering)).to(
            equal("shop/\n  Cart\n    total\n")
        )


with description("a sketch written flat beneath a bare lens marker"):
    with it("should read its shallowest line as the top level"):
        expect(
            SketchOutline(
                "ddd:\n  Customer | custom\n    customer\n", 2
            ).body_for(SketchLens.domain_driven_design)
        ).to(equal("Customer | custom\n  customer\n"))
