"""Every format a fidelity declares, taken there and back with the fidelity's own example.

One behaviour, shared by every practice and fidelity: the example the fidelity names in its practice document is
rendered to each format the fidelity declares and back (``harness.guidance.format_trip.FormatTrip``), and each format
either returns what went in or is one the fidelity says holds less (``leaves_out``). Each fidelity's part below is only
its name; the examples after it name no practice and no format, and a failure names the formats at fault.

Clean Engineering's own fidelities are in ``format_trip_heavy_spec.py``, since drawing a class model takes seconds.
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
        _TRIPS[practice][fidelity] = FormatTrip.of(_TRIPS["made"][practice].fidelities[fidelity]).through_each()
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


with description("the formats Stories declares") as self:
    with context("at the story map"):
        with before.all:
            self.outcomes = _trips_of("stories", "story_map")
            self.fidelity = _TRIPS["made"]["stories"].fidelities["story_map"]

        with included_context("its formats taken there and back"):
            pass

    with context("at scenarios"):
        with before.all:
            self.outcomes = _trips_of("stories", "scenarios")
            self.fidelity = _TRIPS["made"]["stories"].fidelities["scenarios"]

        with included_context("its formats taken there and back"):
            pass

    with context("at acceptance tests"):
        with before.all:
            self.outcomes = _trips_of("stories", "acceptance_tests")
            self.fidelity = _TRIPS["made"]["stories"].fidelities["acceptance_tests"]

        with included_context("its formats taken there and back"):
            pass


with description("the formats DDD declares") as self:
    with context("at the bounded context"):
        with before.all:
            self.outcomes = _trips_of("ddd", "bounded_context")
            self.fidelity = _TRIPS["made"]["ddd"].fidelities["bounded_context"]

        with included_context("its formats taken there and back"):
            pass

    with context("at the model"):
        with before.all:
            self.outcomes = _trips_of("ddd", "model")
            self.fidelity = _TRIPS["made"]["ddd"].fidelities["model"]

        with included_context("its formats taken there and back"):
            pass

    with context("at tactics"):
        with before.all:
            self.outcomes = _trips_of("ddd", "tactics")
            self.fidelity = _TRIPS["made"]["ddd"].fidelities["tactics"]

        with included_context("its formats taken there and back"):
            pass


with description("the formats UX declares") as self:
    with context("at the information architecture"):
        with before.all:
            self.outcomes = _trips_of("ux", "ia")
            self.fidelity = _TRIPS["made"]["ux"].fidelities["ia"]

        with included_context("its formats taken there and back"):
            pass

    with context("at the mockup"):
        with before.all:
            self.outcomes = _trips_of("ux", "mockup")
            self.fidelity = _TRIPS["made"]["ux"].fidelities["mockup"]

        with included_context("its formats taken there and back"):
            pass

    with context("at front-end code"):
        with before.all:
            self.outcomes = _trips_of("ux", "front_end_code")
            self.fidelity = _TRIPS["made"]["ux"].fidelities["front_end_code"]

        with included_context("its formats taken there and back"):
            pass


with description("the formats BDD declares") as self:
    with context("at behavior"):
        with before.all:
            self.outcomes = _trips_of("bdd", "behavior")
            self.fidelity = _TRIPS["made"]["bdd"].fidelities["behavior"]

        with included_context("its formats taken there and back"):
            pass

    with context("at realization"):
        with before.all:
            self.outcomes = _trips_of("bdd", "realization")
            self.fidelity = _TRIPS["made"]["bdd"].fidelities["realization"]

        with included_context("its formats taken there and back"):
            pass

    with context("at development"):
        with before.all:
            self.outcomes = _trips_of("bdd", "development")
            self.fidelity = _TRIPS["made"]["bdd"].fidelities["development"]

        with included_context("its formats taken there and back"):
            pass
