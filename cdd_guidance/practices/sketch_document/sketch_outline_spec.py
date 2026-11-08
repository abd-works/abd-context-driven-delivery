"""BDD spec — a sketch whose hierarchy is carried by markdown headings."""

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("tools", "cdd_guidance/practices", "cdd_guidance/actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import contain, equal, expect
from mamba import before, description, it

from cdd_guidance.practices.sketch_document.discovery_document import DiscoveryDocument
from cdd_guidance.practices.sketch_document.sketch_outline import SketchOutline
from cdd_guidance.practices.bdd.bdd import Bdd
from cdd_guidance.practices.clean_engineering.clean_engineering import CleanEngineering
from cdd_guidance.practices.ddd.ddd import Ddd
from cdd_guidance.practices.stories.stories import Stories
from cdd_guidance.practices.ux.ux import Ux

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
                self.outline.holds(Stories.sketch_lens),
                self.outline.holds(Ddd.sketch_lens),
                self.outline.holds(Ux.sketch_lens),
            ]
        ).to(equal([True, True, False]))

    with description("that is read for one practice"):
        with it("should nest each heading one level deeper than the heading above it"):
            expect(self.outline.body_for(Stories.sketch_lens)).to(
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
            expect("ClientMatched" in self.outline.body_for(Stories.sketch_lens)).to(
                equal(False)
            )

        with it("should nest at the width that practice's notation uses"):
            expect(
                SketchOutline(_HEADED, 2).body_for(Ddd.sketch_lens)
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
            expect(self.outline.body_for(Bdd.sketch_lens)).to(
                equal("")
            )


with description("a sketch that names no lens"):
    with it("should read as one section of indented lines"):
        expect(SketchOutline(_FLAT, 2).body_for(CleanEngineering.sketch_lens)).to(
            equal("shop/\n  Cart\n    total\n")
        )


with description("a sketch written flat beneath a bare lens marker"):
    with it("should read its shallowest line as the top level"):
        expect(
            SketchOutline(
                "ddd:\n  Customer | custom\n    customer\n", 2
            ).body_for(Ddd.sketch_lens)
        ).to(equal("Customer | custom\n  customer\n"))


_OVERVIEW_FIRST = """# Shop — sketch

## Overview

source: checkout interviews

## stories:

### Pay For Cart
"""


with description("a sketch whose header has a section of its own above the practice sections"):
    with it("should take its title from the header"):
        expect(SketchOutline(_OVERVIEW_FIRST).title).to(equal("Shop"))

    with it("should take its sources from anywhere above the first practice section"):
        expect(SketchOutline(_OVERVIEW_FIRST).sources).to(equal("checkout interviews"))

    with description("that a practice writes its discovery document from"):
        with it("should name the sources the sketch's header gives"):
            document = DiscoveryDocument("story-map", "Story Map", _OVERVIEW_FIRST)
            expect(document.lines("Pay For Cart")).to(contain("**Sources / context:** checkout interviews"))

        with it("should head the document with the sketch's title"):
            document = DiscoveryDocument("story-map", "Story Map", _OVERVIEW_FIRST)
            expect(document.lines("Pay For Cart")).to(contain("# Story Map — Shop"))


with description("a sketch that names no lens, read for its header"):
    with it("should have no title, since all of it is one section"):
        expect(SketchOutline(_FLAT).title).to(equal(""))
