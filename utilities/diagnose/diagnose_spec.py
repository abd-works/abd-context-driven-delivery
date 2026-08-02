"""BDD spec for utilities/diagnose/diagnose.py — Diagnose toolset sub-agent dispatch.
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
for _cat in ("primitives", "utilities", "context_tools"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)
sys.modules.pop("diagnose", None)

from expects import contain, equal, expect
from mamba import context, description, it

from diagnose.diagnose import Diagnose


with description("Diagnose toolset"):
    with context("manifest signature"):
        with it("exposes diagnose as a sub_agent tool"):
            # Arrange / Act
            entry = Diagnose.manifest.signature["diagnose"]
            # Assert
            expect(entry["kind"]).to(equal("sub_agent"))

        with it("launches non-blocking"):
            # Arrange / Act
            entry = Diagnose.manifest.signature["diagnose"]
            # Assert
            expect(entry["launch"]).to(equal("non_blocking"))

        with it("returns str"):
            # Arrange / Act
            entry = Diagnose.manifest.signature["diagnose"]
            # Assert
            expect(entry["returns"]).to(equal("str"))

    with context("diagnose sub-agent instructions"):
        with it("describes building a feedback loop in Phase 1"):
            # Arrange / Act
            instructions = Diagnose.manifest.signature["diagnose"]["instructions"]
            # Assert
            expect(instructions).to(contain("Phase 1"))
            expect(instructions).to(contain("feedback loop"))

        with it("requires reproduction before proceeding in Phase 2"):
            # Arrange / Act
            instructions = Diagnose.manifest.signature["diagnose"]["instructions"]
            # Assert
            expect(instructions).to(contain("Phase 2"))
            expect(instructions).to(contain("Reproduce"))

        with it("demands ranked falsifiable hypotheses in Phase 3"):
            # Arrange / Act
            instructions = Diagnose.manifest.signature["diagnose"]["instructions"]
            # Assert
            expect(instructions).to(contain("Phase 3"))
            expect(instructions).to(contain("falsifiable"))

        with it("requires targeted instrumentation in Phase 4"):
            # Arrange / Act
            instructions = Diagnose.manifest.signature["diagnose"]["instructions"]
            # Assert
            expect(instructions).to(contain("Phase 4"))
            expect(instructions).to(contain("Instrument"))

        with it("mandates regression test before fix in Phase 5"):
            # Arrange / Act
            instructions = Diagnose.manifest.signature["diagnose"]["instructions"]
            # Assert
            expect(instructions).to(contain("Phase 5"))
            expect(instructions).to(contain("regression test"))

        with it("requires cleanup and post-mortem in Phase 6"):
            # Arrange / Act
            instructions = Diagnose.manifest.signature["diagnose"]["instructions"]
            # Assert
            expect(instructions).to(contain("Phase 6"))
            expect(instructions).to(contain("post-mortem"))
