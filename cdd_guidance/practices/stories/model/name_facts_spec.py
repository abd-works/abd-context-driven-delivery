"""What a story's name says about it, as the story map's rules read it."""

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[4]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from expects import equal, expect
from mamba import context, description, it

from cdd_guidance.practices.stories.model.name_facts import opening_of


with description("a story name read for its opening word"):
    with context("that opens with a verb ending the way a nominalisation ends"):
        with it("should read comment as a verb, since Comment On A Story Card says what the person does"):
            expect(opening_of("Comment On A Story Card")).to(equal(("comment", "verb")))

    with context("that opens with a noun made from a verb"):
        with it("should read payment as a nominalisation"):
            expect(opening_of("Payment Of An Order")).to(equal(("payment", "nominalisation")))
