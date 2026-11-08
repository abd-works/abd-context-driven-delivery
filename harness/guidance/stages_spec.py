"""The stages of the CDD approach, each with its scope and the actions a person runs on a fidelity in it."""
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import be_none, equal, expect
from mamba import description, it

from harness.guidance.stages import REVIEW, STAGES
from harness.guidance.action_catalogue import ActionCatalogue
from harness.guidance.practice_catalogue import PracticeCatalogue
from harness.installation.destination import data_of
import cdd_guidance.practices  # noqa: F401 - registers the practices with the practice catalogue
import cdd_guidance.actions  # noqa: F401 - registers the actions with the action catalogue


with description("the stages of the approach"):
    with it("should walk Discovery, Specification, and Implementation in order"):
        expect([stage.title for stage in STAGES]).to(equal(["Discovery", "Specification", "Implementation"]))

    with it("should hold every stage a practice's fidelity names"):
        named = {fidelity.stage for practice in PracticeCatalogue.practices() for fidelity in practice.fidelities}
        expect(named - set(STAGES.names)).to(equal(set()))

    with it("should find a stage by the name a fidelity gives it"):
        expect(STAGES.of("specification").title).to(equal("Specification"))

    with it("should find no stage for a name that is no stage"):
        expect(STAGES.of("exploration")).to(be_none)

    with description("a stage's scope"):
        with it("should narrow and deepen along the board"):
            expect([stage.scope.reach for stage in STAGES]).to(
                equal(["wide / shallow", "narrow / deeper", "narrowest / deep"])
            )

        with it("should send its shape, name, reach, and what it covers as data"):
            expect(data_of(STAGES.of("discovery").scope)).to(equal({
                "shape": "solution", "name": "Whole solution", "reach": "wide / shallow",
                "covers": "outcomes · scope · boundaries",
            }))

    with description("a stage's actions"):
        with it("should take every fidelity through generate, validate, and review"):
            expect(STAGES.of("discovery").steps).to(equal(["generate", "validate", "review"]))

        with it("should offer the other actions after the steps"):
            expect(STAGES.of("discovery").actions).to(
                equal(["generate", "validate", "review", "iterate", "sketch", "render", "document"])
            )

        with it("should name only actions in the action catalogue, besides the person's review"):
            unknown = {action for stage in STAGES for action in stage.actions if action != REVIEW} - set(ActionCatalogue.names())
            expect(unknown).to(equal(set()))

        with it("should name generate and render as the actions that take the formats a person picks"):
            expect(STAGES.of("specification").actions_with_formats).to(equal(["generate", "render"]))

        with it("should leave validate and review out of the actions that write a fidelity's files"):
            expect(STAGES.of("implementation").producing_actions).to(
                equal(["generate", "iterate", "sketch", "render", "document"])
            )
