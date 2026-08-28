# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""BDD development specs for GatedWidget - greeting roster and fixture surface."""
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[5]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("primitives", "utilities", "context_tools", "context_tools/actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)
sys.modules.pop("tools", None)

from expects import contain, equal, expect
from mamba import before, context, description, it

from tools.hooks.examples.gated_widget.gated_widget import GatedWidget


with description("a gated widget"):
    with context("that has been created"):
        with before.each:
            self.widget = GatedWidget()

        with it("should expose the default label"):
            # Assert
            expect(self.widget.label).to(equal("widget"))

        with context("that is renamed"):
            with it("should return a renamed confirmation"):
                # Act
                result = self.widget.rename("probe")
                # Assert
                expect(result).to(equal("renamed to probe"))

            with it("should expose the new label"):
                # Act
                self.widget.rename("probe")
                # Assert
                expect(self.widget.label).to(equal("probe"))

        with context("that acknowledges compliance"):
            with it("should confirm edits are cleared for the session"):
                # Act
                result = self.widget.satisfy()
                # Assert
                expect(result).to(contain("compliance acknowledged"))

        with context("that launches a revision bump"):
            with it("should describe the background edit the sub-agent must perform"):
                # Assert — docstring is the agent contract for this fixture tool
                expect(self.widget.launch_revision_bump.__doc__).to(
                    contain("_REVISION = 2")
                )

    with context("that has not greeted anyone"):
        with before.each:
            self.widget = GatedWidget()

        with context("that is asked who is here"):
            with it("should report that no one has said hello yet"):
                # Act
                result = self.widget.whos_all_here()
                # Assert
                expect(result).to(equal("No one has said hello yet."))

        with context("that is bid farewell"):
            with it("should echo the farewell without naming anyone"):
                # Act
                result = self.widget.goodbye("See you soon")
                # Assert — empty roster keeps "goodbye" lowercase after the farewell
                expect(result).to(contain("See you soon! goodbye to everyone"))

    with context("that has greeted callers"):
        with before.each:
            self.widget = GatedWidget()
            self.widget.hello_world("Ada")
            self.widget.hello_world("Grace")

        with context("that greets someone"):
            with it("should introduce the widget to that person"):
                # Arrange
                widget = GatedWidget()
                # Act
                result = widget.hello_world("Ada")
                # Assert
                expect(result).to(contain("Hello, Ada!"))

        with context("that is asked who is here"):
            with it("should list everyone who was greeted"):
                # Act
                result = self.widget.whos_all_here()
                # Assert
                expect(result).to(equal("Everyone who's here: Ada, Grace."))

        with context("that greets the same person again"):
            with it("should still list that person only once"):
                # Act
                self.widget.hello_world("Ada")
                result = self.widget.whos_all_here()
                # Assert
                expect(result).to(equal("Everyone who's here: Ada, Grace."))

        with context("that is bid farewell"):
            with it("should name everyone who was greeted"):
                # Act
                result = self.widget.goodbye("See you soon")
                # Assert
                expect(result).to(contain("Goodbye, Ada, Grace, and "))
