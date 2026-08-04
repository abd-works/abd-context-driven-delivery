# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""BDD development specs for LoggedProbe - usage order; describes are conditions, not hubs."""
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("primitives", "utilities", "context_tools"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)
sys.modules.pop("tools", None)
sys.modules.pop("sessions", None)

from expects import be_false, be_true, equal, expect
from mamba import before, context, description, it

from workspace import is_logged
from tools.examples.logged_probe import LoggedProbe


with description("a tool that is annotated with log"):
    with context("that is invoked"):
        with before.each:
            self.probe = LoggedProbe()

        with it("should echo the message with a pong prefix"):
            # Arrange
            message = "hello"
            # Act
            result = self.probe.ping(message)
            # Assert
            expect(result).to(equal("pong:hello"))

    with context("that is inspected for log annotation"):
        with it("should be recognized as a logged member"):
            expect(is_logged(LoggedProbe.ping)).to(be_true)


with description("a tool that is not annotated with log"):
    with context("that is invoked"):
        with before.each:
            self.probe = LoggedProbe()

        with it("should return silent"):
            # Act
            result = self.probe.quiet()
            # Assert
            expect(result).to(equal("silent"))

    with context("that is inspected for log annotation"):
        with it("should not be recognized as a logged member"):
            expect(is_logged(LoggedProbe.quiet)).to(be_false)


with description("an action that is annotated with log"):
    with context("that is invoked"):
        with before.each:
            self.probe = LoggedProbe()

        with it("should return told"):
            # Act
            result = self.probe.narrate("hello")
            # Assert
            expect(result).to(equal("told"))

    with context("that is inspected for log annotation"):
        with it("should be recognized as a logged member"):
            expect(is_logged(LoggedProbe.narrate)).to(be_true)


with description("an action that is not annotated with log"):
    with context("that is invoked"):
        with before.each:
            self.probe = LoggedProbe()

        with it("should return muted"):
            # Act
            result = self.probe.mute()
            # Assert
            expect(result).to(equal("muted"))

    with context("that is inspected for log annotation"):
        with it("should not be recognized as a logged member"):
            expect(is_logged(LoggedProbe.mute)).to(be_false)
