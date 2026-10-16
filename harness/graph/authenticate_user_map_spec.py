"""The authenticate-user sample map holds the real stories only."""

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from expects import equal, expect
from mamba import description, it

_STORY = (
    _REPO
    / "harness"
    / "graph"
    / "examples"
    / "input"
    / "tests"
    / "onboard-a-customer"
    / "authenticate-user"
    / "authenticate_user.story.shared.ts"
)


with description("authenticate-user story map"):
    with it("should keep only the authenticate-user stories"):
        text = _STORY.read_text(encoding="utf-8")
        expect("shareStory('Handle Request'" in text).to(equal(False))
        expect("shareStory('Submit Order'" in text).to(equal(False))
        expect("shareStory('Submit Orders'" in text).to(equal(False))
        expect("shareStory('Create Account'" in text).to(equal(True))
        expect("shareStory('Enter Validation Code'" in text).to(equal(True))
        expect("shareStory('Sign In With Existing Account'" in text).to(equal(True))
