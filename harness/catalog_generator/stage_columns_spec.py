"""BDD specs for the catalog board's stage columns and ticket labels."""
from expects import be_none, equal, expect
from mamba import context, description, it

from harness.catalog_generator.stage_columns import STAGE_COLUMNS, BoardLabel
from harness.guidance.stages import STAGES


with description("the catalog board's stage columns"):
    with it("should walk the approach's stages in order"):
        expect(STAGE_COLUMNS.stages).to(equal(("discovery", "specification", "implementation")))

    with it("should give the specification column its key in the page markup"):
        expect(STAGE_COLUMNS.of(STAGES.of("specification")).key).to(equal("spec"))

    with it("should have no column for no stage"):
        expect(STAGE_COLUMNS.of(STAGES.of("validate"))).to(be_none)


with description("a board ticket's label"):
    with context("for a fidelity name in snake case"):
        with it("should be the name in kebab case"):
            expect(str(BoardLabel("story_map"))).to(equal("story-map"))

    with context("for an abbreviation the board writes out"):
        with it("should be the words it stands for"):
            expect(str(BoardLabel("ia"))).to(equal("information-architecture"))
