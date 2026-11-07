"""Approach page copy lives in markdown so it can be hand-edited."""
import tempfile
from pathlib import Path

from expects import equal, expect
from mamba import before, context, description, it

from harness.catalog_generator.approach_copy import APPROACH_MARKDOWN, ApproachCopy

_MINIMAL_MD = """# Approach

HAND-EDITABLE-SUBHEAD

## Stages

### Context

id: context
shape: square
scope_name: Context
scope_width: square
items: Business Model | User Traction | Operating Benchmarks

HAND-EDITABLE-STAGE-COPY

## Context Driven Delivery Practices

### Product Engineering

slug: product-engineering
kind: descriptions

- HAND-EDITABLE-BULLET

See [the stories](stories.md).

## Library

HAND-EDITABLE-LIBRARY
"""

_BOARD_STAGE_MD = """# Approach

Subhead

## Stages

### Discovery

id: discovery
items: ZZ-CHIP

ZZ-PARA

### Specification

id: specification
items: Spec Chip

Spec paragraph

### Implement

id: implementation
items: Engineer Chip

Engineer paragraph
"""


def _copy(markdown: str) -> ApproachCopy:
    path = Path(tempfile.mkdtemp()) / "cdd-approach.md"
    path.write_text(markdown, encoding="utf-8")
    return ApproachCopy.load(path)


with description("the approach page's copy"):
    with context("read from hand-edited markdown"):
        with before.all:
            self.copy = _copy(_MINIMAL_MD)

        with it("should read the subhead from the intro"):
            expect(self.copy.subhead).to(equal("HAND-EDITABLE-SUBHEAD"))

        with it("should read the principles heading"):
            expect(self.copy.principles_heading).to(equal("Context Driven Delivery Practices"))

        with it("should read the library heading"):
            expect(self.copy.library_heading).to(equal("HAND-EDITABLE-LIBRARY"))

        with it("should read each stage's settings"):
            expect(self.copy.stages[0].id).to(equal("context"))

        with it("should read each stage's paragraphs"):
            expect(self.copy.stages[0].paras).to(equal(("HAND-EDITABLE-STAGE-COPY",)))

        with it("should read each principle's bullets"):
            expect(self.copy.principles[0].bullets).to(equal(("HAND-EDITABLE-BULLET",)))

        with it("should write a principle's caption links as HTML"):
            expect(self.copy.principles[0].caption).to(equal('See <a href="stories.md">the stories</a>.'))

        with it("should keep the scope a stage of the page alone gives in its settings"):
            scope = self.copy.stages[0].scope
            expect((scope.shape, scope.name, scope.reach)).to(equal(("square", "Context", "square")))

    with context("whose stages are the approach's own"):
        with before.all:
            self.copy = _copy(_BOARD_STAGE_MD)

        with it("should take a CDD stage's scope from the approach's stages"):
            scope = self.copy.stages[0].scope
            expect((scope.shape, scope.name, scope.reach)).to(equal(("solution", "Whole solution", "wide / shallow")))

        with it("should give the board each stage by its column's key"):
            expect(self.copy.board_stages["spec"].items).to(equal(("Spec Chip",)))

    with context("kept beside the catalog generator"):
        with it("should open with the harness sentence"):
            expect("CDD harness" in ApproachCopy.load(APPROACH_MARKDOWN).subhead).to(equal(True))
