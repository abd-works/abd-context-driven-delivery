"""Every format a fidelity declares, taken there and back with the fidelity's own example.

One behaviour, shared by every practice and fidelity: the example the fidelity names in its practice document is
rendered to each format the fidelity declares and back (``harness.guidance.format_trip.FormatTrip``), and each format
either returns what went in or is one the fidelity says holds less (``leaves_out``). Each fidelity's part below is only
its name; the examples after it name no practice and no format, and a failure names the formats at fault.

The other four practices are in ``format_trip_spec.py``; these draw a class model, which takes seconds.
"""

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from expects import equal, expect
from mamba import before, context, description, included_context, it, shared_context

import cdd_guidance.practices  # noqa: F401  (registers the practices)
from harness.guidance.format_trip import NO_EXAMPLE, FormatTrip
from harness.guidance.practice_catalogue import PRACTICE_CATALOGUE

_TRIPS: dict[str, dict] = {}


def _trips_of(practice: str, fidelity: str) -> dict:
    """What each format the fidelity declares came to, with the practices made once for every fidelity asked."""
    if not _TRIPS:
        _TRIPS.update({made.key: {} for made in PRACTICE_CATALOGUE.create_all()})
        _TRIPS["made"] = {made.key: made for made in PRACTICE_CATALOGUE.create_all()}
    if fidelity not in _TRIPS[practice]:
        _TRIPS[practice][fidelity] = FormatTrip.outcomes_of(_TRIPS["made"][practice].fidelities[fidelity])
    return _TRIPS[practice][fidelity]


with shared_context("its formats taken there and back"):
    with it("should name the example its formats are taken there and back with"):
        expect([format for format, outcome in self.outcomes.items() if outcome.status == NO_EXAMPLE]).to(equal([]))

    with it("should have each format return what went in, or say what the format does not hold"):
        failing = {format: f"{outcome} {outcome.refused or list(outcome.lost[:3])}" for format, outcome in self.outcomes.items() if not outcome.passes}
        expect(failing).to(equal({}))

    with it("should say what a format leaves out only for a format that holds less"):
        idle = [format for format, said in self.fidelity.leaves_out.items() if format in self.outcomes and not self.outcomes[format].lost]
        expect(idle).to(equal([]))


with description("the formats Clean Engineering declares") as self:
    with context("at modules"):
        with before.all:
            self.outcomes = _trips_of("clean_engineering", "modules")
            self.fidelity = _TRIPS["made"]["clean_engineering"].fidelities["modules"]

        with included_context("its formats taken there and back"):
            pass

    with context("at the model"):
        with before.all:
            self.outcomes = _trips_of("clean_engineering", "model")
            self.fidelity = _TRIPS["made"]["clean_engineering"].fidelities["model"]

        with included_context("its formats taken there and back"):
            pass

    with context("at code"):
        with before.all:
            self.outcomes = _trips_of("clean_engineering", "code")
            self.fidelity = _TRIPS["made"]["clean_engineering"].fidelities["code"]

        with included_context("its formats taken there and back"):
            pass
