"""
# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# Agent reading this file: run line 1 manifest, then python -m tools run -.  Follow response.instructions only.
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""
import sys
from pathlib import Path

from expects import be_true, equal, expect, raise_error
from mamba import before, context, description, it

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("primitives", "utilities", "context_tools"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from primitives.actions.action import action
from primitives.focus._decorator import focus
from primitives.instructions.instructions import instruction


# ---------------------------------------------------------------------------
# Minimal stubs used by the tests
# ---------------------------------------------------------------------------

@action
def _stub_action(self) -> None:
    """stub action"""


@instruction
def _stub_instruction(self) -> str:
    """stub instruction"""
    return ""


def _plain_function() -> None:
    pass


# ---------------------------------------------------------------------------
# Specs
# ---------------------------------------------------------------------------

with description("a method annotated to bind a focus group"):

    with context("that is applied to an @action method"):
        with before.each:
            @action
            def act(self) -> None:
                """act"""

            self.decorated = focus(act, focus="fidelities")

        with it("should record the focus group entry on the action"):
            entries = getattr(self.decorated, "_focus_entries", [])
            expect(len(entries)).to(equal(1))
            group, key = entries[0]
            expect(group).to(equal("fidelities"))

        with it("should derive the filter key by converting ies suffix to y"):
            entries = getattr(self.decorated, "_focus_entries", [])
            group, key = entries[0]
            expect(key).to(equal("fidelity"))

    with context("that is applied to an @action method with a trailing-s group name"):
        with before.each:
            @action
            def act(self) -> None:
                """act"""

            self.decorated = focus(act, focus="formats")

        with it("should strip the trailing s to derive the filter key"):
            entries = getattr(self.decorated, "_focus_entries", [])
            group, key = entries[0]
            expect(key).to(equal("format"))

    with context("that is applied to an @action method with an explicit filter_key"):
        with before.each:
            @action
            def act(self) -> None:
                """act"""

            self.decorated = focus(act, focus="modes", filter_key="mode_override")

        with it("should use the provided filter key instead of deriving one"):
            entries = getattr(self.decorated, "_focus_entries", [])
            group, key = entries[0]
            expect(key).to(equal("mode_override"))

    with context("that is applied twice to the same @action method"):
        with before.each:
            @action
            def act(self) -> None:
                """act"""

            self.decorated = focus(focus(act, focus="fidelities"), focus="formats")

        with it("should accumulate both focus entries"):
            entries = getattr(self.decorated, "_focus_entries", [])
            expect(len(entries)).to(equal(2))

        with it("should preserve the first focus group name"):
            entries = getattr(self.decorated, "_focus_entries", [])
            expect(entries[0][0]).to(equal("fidelities"))

        with it("should preserve the second focus group name"):
            entries = getattr(self.decorated, "_focus_entries", [])
            expect(entries[1][0]).to(equal("formats"))

    with context("that is applied to an @instruction method"):
        with before.each:
            @instruction
            def instr(self) -> str:
                """instr"""
                return ""

            self.decorated = focus(instr, focus="fidelities")

        with it("should record the focus group entry"):
            entries = getattr(self.decorated, "_focus_entries", [])
            expect(len(entries)).to(equal(1))

        with it("should set _instruction_group to the focus group name"):
            group = getattr(self.decorated, "_instruction_group", None)
            expect(group).to(equal("fidelities"))

        with it("should set _instruction_filter_key using the derived key"):
            key = getattr(self.decorated, "_instruction_filter_key", None)
            expect(key).to(equal("fidelity"))

    with context("that is applied to a plain function"):
        with it("should raise TypeError"):
            expect(lambda: focus(_plain_function, focus="fidelities")).to(
                raise_error(TypeError)
            )

    with context("that is used as a decorator factory (no positional func)"):
        with before.each:
            @action
            def act(self) -> None:
                """act"""

            decorator = focus(focus="modes")
            self.decorated = decorator(act)

        with it("should return a callable decorator when no func is given"):
            entries = getattr(self.decorated, "_focus_entries", [])
            expect(len(entries)).to(equal(1))

        with it("should derive the filter key for the modes group"):
            entries = getattr(self.decorated, "_focus_entries", [])
            group, key = entries[0]
            expect(key).to(equal("mode"))
