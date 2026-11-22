"""The action catalogue: every action CDD ships, found from the action folders."""
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import be_false, be_true, contain, equal, expect
from mamba import before, description, it

from harness.guidance.action_catalogue import ACTION_CATALOGUE
import cdd_guidance.practices  # noqa: F401 - registers the practices with the practice catalogue
import cdd_guidance.actions  # noqa: F401 - registers the actions with the action catalogue

_ACTIONS_FOLDER = _REPO_ROOT / "cdd_guidance" / "actions"


def _action_named(name: str):
    return next(action for action in ACTION_CATALOGUE.actions if action.name == name)


with description("the action catalogue"):
    with before.all:
        self.names = ACTION_CATALOGUE.names

    with it("should hold a toolset for every action folder"):
        folders = sorted(
            folder.name for folder in _ACTIONS_FOLDER.iterdir() if folder.is_dir() and folder.name[0] not in "_."
        )
        expect([toolset.__module__.split(".")[-1] for toolset in ACTION_CATALOGUE.toolsets]).to(equal(folders))

    with it("should list each operation a toolset publishes as a skill"):
        expect(self.names).to(contain("generate", "validate", "sketch", "render", "grill", "partition"))

    with it("should list every skill of a toolset that installs several"):
        expect(self.names).to(contain("repair", "verify_fix"))

    with it("should leave out a toolset's tools that are not skills"):
        expect("generate_fixes_from_validate" in self.names).to(be_false)

    with it("should leave out a skill that is never installed"):
        expect("create_rule" in self.names).to(be_false)

    with it("should leave out the folder of examples"):
        expect("CarStory" in [toolset.__name__ for toolset in ACTION_CATALOGUE.toolsets]).to(be_false)

    with description("that holds each action"):
        with it("should give the toolset that installs it"):
            expect(_action_named("verify_fix").toolset_class.__name__).to(equal("Improvement"))

        with it("should give the toolset's folder"):
            expect(_action_named("grill").folder.name).to(equal("grill_context"))

        with it("should list no name that no toolset publishes"):
            expect(("repair" in self.names, "review" in self.names)).to(equal((True, False)))

    # Every stage offers the same actions on a fidelity, so the catalogue answers them once, by each action's @on_stage.
    with description("that places the actions a person runs on a fidelity in its stage"):
        with it("should take every fidelity through generate, then validate"):
            expect([action.name for action in ACTION_CATALOGUE.steps]).to(equal(["generate", "validate"]))

        with it("should name generate the step that writes and validate the step that checks"):
            expect((ACTION_CATALOGUE.writing_step.name, ACTION_CATALOGUE.checking_step.name)).to(equal(("generate", "validate")))

        with it("should offer the other actions after the steps"):
            expect([action.name for action in ACTION_CATALOGUE.on_fidelities]).to(
                equal(["partition", "generate", "validate", "iterate", "sketch", "render", "document"])
            )

        with it("should name generate and render as the actions that take the formats a person picks"):
            expect([action.name for action in ACTION_CATALOGUE.taking_formats]).to(equal(["generate", "render"]))

        with it("should leave validate out of the actions that write a fidelity's files"):
            expect([action.name for action in ACTION_CATALOGUE.producing]).to(
                equal(["partition", "generate", "iterate", "sketch", "render", "document"])
            )

        with it("should name validate and render as the actions that wait until a fidelity has output"):
            expect([action.name for action in ACTION_CATALOGUE.needing_output]).to(equal(["validate", "render"]))

        with it("should give an action run on no fidelity's stage no place"):
            expect(_action_named("repair").place).to(equal(None))
