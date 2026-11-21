"""A story's name says it is a one-time task only when it says the work happens once and is then done."""

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[4]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from expects import equal, expect
from mamba import context, description, it

from cdd_guidance.practices.stories.model.name_facts import names_one_time_task


def _one_time(*names: str) -> list[bool]:
    return [names_one_time_task(name) for name in names]


with description("a story name read for a one-time task"):
    with context("that says the work is done once and is then over"):
        with it("should read a name that ends in once as a one-time task"):
            expect(_one_time("Rename Ticket Columns Once", "Import Old Tickets Once Only")).to(equal([True, True]))

        with it("should read a one-time setup or migration as a one-time task"):
            expect(_one_time("Run One-Time Import", "Do Initial Setup", "Migrate Legacy Tickets")).to(equal([True, True, True]))

    with context("that says how often the work happens each time the behaviour runs"):
        with it("should read once per, once for each and once by as a repeatable behaviour"):
            names = ("Check Ticket Branches Once Per Board Build", "Read Session File Once For Each Board Build", "Store Each Screenshot Once By Content Hash")
            expect(_one_time(*names)).to(equal([False, False, False]))

    with context("that uses once to mean as soon as"):
        with it("should read the name as a repeatable behaviour"):
            expect(_one_time("Reattach A Screen Once Its Change Reaches Production")).to(equal([False]))

    with context("that does not mention once"):
        with it("should read the name as a repeatable behaviour"):
            expect(_one_time("Delete Ticket", "")).to(equal([False, False]))
