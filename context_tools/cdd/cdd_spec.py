"""BDD spec for context_tools/cdd/cdd.py — stage menu and child tool wiring.
# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("context_tools", "primitives", "utilities"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import be_true, equal, expect, raise_error
from mamba import before, context, description, it

from primitives.actions.action import _ActionExpander
from context_tools.bdd.bdd import Bdd
from context_tools.cdd.cdd import Cdd
from context_tools.clean_engineering.clean_engineering import CleanEngineering
from context_tools.ddd.ddd import Ddd
from context_tools.stories.stories import Stories
from context_tools.ux.ux import Ux


with description("a CDD orchestrator"):
    with context("that is created"):
        with context("with discovery fidelity"):
            with before.each:
                self.cdd = Cdd(fidelity="discovery")

            with it("should default format to markdown"):
                expect(self.cdd.format).to(equal("markdown"))

            with it("should retain fidelity discovery"):
                expect(self.cdd.fidelity).to(equal("discovery"))

        with context("with spec fidelity"):
            with it("should default format to python"):
                expect(Cdd(fidelity="spec").format).to(equal("python"))

        with context("with engineer fidelity"):
            with it("should default format to python"):
                expect(Cdd(fidelity="engineer").format).to(equal("python"))

        with context("with an unsupported fidelity"):
            with it("should raise ValueError"):
                expect(lambda: Cdd(fidelity="modules")).to(raise_error(ValueError))

    with context("that resolves context tools for discovery"):
        with before.each:
            self.tools = Cdd(fidelity="discovery").context_tools()
            self.pairs = [(type(t), t.fidelity) for t in self.tools]

        with it("should return four child tools"):
            expect(len(self.tools)).to(equal(4))

        with it("should wire Stories at story_map"):
            expect(self.pairs[0]).to(equal((Stories, "story_map")))

        with it("should wire Ddd at bounded_context"):
            expect(self.pairs[1]).to(equal((Ddd, "bounded_context")))

        with it("should wire Ux at ia"):
            expect(self.pairs[2]).to(equal((Ux, "ia")))

        with it("should wire CleanEngineering at modules"):
            expect(self.pairs[3]).to(equal((CleanEngineering, "modules")))

        with it("should omit Bdd"):
            expect(any(isinstance(t, Bdd) for t in self.tools)).to(equal(False))

    with context("that resolves context tools for explore"):
        with it("should raise ValueError (explore stage no longer exists)"):
            expect(lambda: Cdd(fidelity="explore")).to(raise_error(ValueError))

    with context("that resolves context tools for spec"):
        with before.each:
            self.pairs = [
                (type(t), t.fidelity) for t in Cdd(fidelity="spec").context_tools()
            ]

        with it("should wire children at building_blocks / scenarios / mockup / model / behavior"):
            expect(self.pairs).to(
                equal(
                    [
                        (Ddd, "building_blocks"),
                        (Stories, "scenarios"),
                        (Ux, "mockup"),
                        (CleanEngineering, "model"),
                        (Bdd, "behavior"),
                    ]
                )
            )

    with context("that resolves context tools for engineer"):
        with before.each:
            self.pairs = [
                (type(t), t.fidelity)
                for t in Cdd(fidelity="engineer").context_tools()
            ]

        with it("should include Ux at front_end_code and Bdd at development"):
            expect(self.pairs).to(
                equal(
                    [
                        (Ddd, "tactics"),
                        (Stories, "acceptance_tests"),
                        (Ux, "front_end_code"),
                        (CleanEngineering, "code"),
                        (Bdd, "development"),
                    ]
                )
            )

    with context("that does not own kit lifecycle actions"):
        with it("should not expose generate, validate, satisfy, repair, grill, sketch, iterate, or document"):
            host = Cdd(fidelity="discovery")
            for name in (
                "generate",
                "validate",
                "satisfy",
                "repair",
                "grill",
                "sketch",
                "iterate",
                "document",
            ):
                expect(name in host.actions).to(equal(False))

    with context("whose guidance action is expanded"):
        with before.each:
            self.cdd = Cdd(fidelity="discovery")
            self.body = _ActionExpander.instance().parse_body(Cdd.guidance, self.cdd)
            self.joined = "\n".join(self.body.prose_parts)

        with it("should defer each child as a separate tools run"):
            expect(self.joined.count("Separate tools run") >= 4).to(be_true)

        with it("should not inline CleanEngineering recipes"):
            expect("Deepen OO design" in self.joined).to(equal(False))

        with it("should name Stories among the deferred runs"):
            expect("context_tools.stories.stories:Stories" in self.joined).to(be_true)

        with it("should tell the caller to call child guidance and pass each child to this action"):
            expect("Call guidance" in self.joined).to(be_true)
            expect("pass that child to this action" in self.joined).to(be_true)
            expect("already knows what to do" in self.joined).to(be_true)

    with context("whose contexts slot is expanded"):
        with it("should include the order-themes-by-journey rule slug"):
            expect("order-themes-by-journey" in Cdd().contexts().expand()).to(be_true)
