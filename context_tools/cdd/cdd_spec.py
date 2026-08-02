"""BDD spec for context_tools/cdd/cdd.py — stage menu and child tool wiring.
# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
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

        with context("with explore fidelity"):
            with it("should default format to markdown"):
                expect(Cdd(fidelity="explore").format).to(equal("markdown"))

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

        with it("should wire Stories at discovery"):
            expect(self.pairs[0]).to(equal((Stories, "discovery")))

        with it("should wire Ddd at bounded_context"):
            expect(self.pairs[1]).to(equal((Ddd, "bounded_context")))

        with it("should wire Ux at ia"):
            expect(self.pairs[2]).to(equal((Ux, "ia")))

        with it("should wire CleanEngineering at modules"):
            expect(self.pairs[3]).to(equal((CleanEngineering, "modules")))

        with it("should omit Bdd"):
            expect(any(isinstance(t, Bdd) for t in self.tools)).to(equal(False))

    with context("that resolves context tools for explore"):
        with before.each:
            self.tools = Cdd(fidelity="explore").context_tools()
            self.pairs = [(type(t), t.fidelity) for t in self.tools]

        with it("should include Bdd at behavior after CleanEngineering"):
            expect(self.pairs).to(
                equal(
                    [
                        (Ddd, "building_blocks"),
                        (Stories, "exploration"),
                        (Ux, "mockup"),
                        (CleanEngineering, "model"),
                        (Bdd, "behavior"),
                    ]
                )
            )

    with context("that resolves context tools for spec"):
        with before.each:
            self.pairs = [
                (type(t), t.fidelity) for t in Cdd(fidelity="spec").context_tools()
            ]

        with it("should wire children at code / exploration / mockup / development"):
            expect(self.pairs).to(
                equal(
                    [
                        (Ddd, "code"),
                        (Stories, "exploration"),
                        (Ux, "mockup"),
                        (CleanEngineering, "code"),
                        (Bdd, "development"),
                    ]
                )
            )

    with context("that resolves context tools for engineer"):
        with before.each:
            self.pairs = [
                (type(t), t.fidelity)
                for t in Cdd(fidelity="engineer").context_tools()
            ]

        with it("should omit Ux and keep Bdd at development"):
            expect(self.pairs).to(
                equal(
                    [
                        (Ddd, "code"),
                        (Stories, "engineering"),
                        (CleanEngineering, "code"),
                        (Bdd, "development"),
                    ]
                )
            )

    with context("whose lifecycle actions walk the stage tools"):
        with before.each:
            self.cdd = Cdd(fidelity="discovery")

        with it("should expose generate_output as a callable action"):
            expect(callable(self.cdd.generate_output)).to(be_true)

        with it("should expose grill as a callable action"):
            expect(callable(self.cdd.grill)).to(be_true)

        with it("should expose sketch as a callable action"):
            expect(callable(self.cdd.sketch)).to(be_true)

        with it("should expose iterate as a callable action"):
            expect(callable(self.cdd.iterate)).to(be_true)

        with it("should expose validate as a callable action"):
            expect(callable(self.cdd.validate)).to(be_true)

        with it("should expose satisfy as a callable action"):
            expect(callable(self.cdd.satisfy)).to(be_true)

        with it("should expose document as a callable action"):
            expect(callable(self.cdd.document)).to(be_true)
