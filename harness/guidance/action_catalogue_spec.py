"""The action catalogue: every action CDD ships, found from the action folders."""
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import be_false, be_none, be_true, contain, equal, expect
from mamba import before, description, it

from harness.guidance.action_catalogue import ActionCatalogue

_ACTIONS_FOLDER = _REPO_ROOT / "cdd_guidance" / "actions"


with description("the action catalogue"):
    with before.all:
        self.names = ActionCatalogue.names()

    with it("should hold a kit for every action folder"):
        folders = sorted(
            folder.name for folder in _ACTIONS_FOLDER.iterdir() if folder.is_dir() and folder.name[0] not in "_."
        )
        expect([kit.__module__.split(".")[-1] for kit in ActionCatalogue.kits()]).to(equal(folders))

    with it("should list each operation a kit publishes as a skill"):
        expect(self.names).to(contain("generate", "validate", "sketch", "render", "grill", "partition"))

    with it("should list every skill of a kit that publishes several"):
        expect(self.names).to(contain("validate", "createRule", "repair", "verify_fix"))

    with it("should leave out a kit's tools that are not skills"):
        expect("generate_fixes_from_validate" in self.names).to(be_false)

    with it("should leave out the folder of examples"):
        expect("CarStory" in [kit.__name__ for kit in ActionCatalogue.kits()]).to(be_false)

    with description("that is asked for one action"):
        with it("should give the kit that publishes it"):
            expect(ActionCatalogue.action("createRule").kit_class.__name__).to(equal("Validate"))

        with it("should give the kit's folder"):
            expect(ActionCatalogue.action("grill").folder.name).to(equal("grill_context"))

        with it("should give nothing for a name no kit publishes"):
            expect(ActionCatalogue.action("astrology")).to(be_none)

        with it("should say whether a kit publishes the name"):
            expect((ActionCatalogue.has("repair"), ActionCatalogue.has("review"))).to(equal((True, False)))
