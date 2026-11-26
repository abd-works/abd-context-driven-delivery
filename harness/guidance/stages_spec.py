"""The stages of the CDD approach, each with its scope; the actions a person runs on a fidelity are the action catalogue's."""
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import be_none, equal, expect
from mamba import description, it

from harness.guidance.stages import STAGES
from harness.guidance.practice_catalogue import PRACTICE_CATALOGUE
from harness.installation.data_class import data_of
import cdd_guidance.practices  # noqa: F401 - registers the practices with the practice catalogue


with description("the stages of the approach"):
    with it("should walk Discovery, Specification, Implementation, and Hardening in order"):
        expect([stage.title for stage in STAGES]).to(equal(["Discovery", "Specification", "Implementation", "Hardening"]))

    with it("should hold every stage a practice's fidelity names"):
        named = {fidelity.stage for practice in PRACTICE_CATALOGUE.create_all() for fidelity in practice.fidelities}
        expect(named - set(STAGES.names)).to(equal(set()))

    with it("should find a stage by the name a fidelity gives it"):
        expect(STAGES.of("specification").title).to(equal("Specification"))

    with it("should find no stage for a name that is no stage"):
        expect(STAGES.of("exploration")).to(be_none)

    with description("a stage's scope"):
        with it("should narrow and deepen along the board"):
            expect([stage.scope.reach for stage in STAGES]).to(
                equal(["wide / shallow", "narrow / deeper", "narrowest / deep", "wide / deep"])
            )

        with it("should take in the whole release for Hardening, to make it ready for production"):
            expect(data_of(STAGES.of("hardening").scope)).to(equal({
                "shape": "release", "name": "Whole release", "reach": "wide / deep",
                "covers": "exploration · regression · readiness",
            }))

        with it("should send its shape, name, reach, and what it covers as data"):
            expect(data_of(STAGES.of("discovery").scope)).to(equal({
                "shape": "solution", "name": "Whole solution", "reach": "wide / shallow",
                "covers": "outcomes · scope · boundaries",
            }))
