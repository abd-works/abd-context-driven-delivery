"""A practice's schema and its fidelities: each node type the schema declares belongs to fidelities the practice has."""
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import equal, expect
from mamba import context, description, it

from harness.guidance.practice_catalogue import PracticeCatalogue
import cdd_guidance.practices  # noqa: F401 - registers the practices with the practice catalogue
import cdd_guidance.actions  # noqa: F401 - registers the actions with the action catalogue


def _fidelity_errors(practice) -> list[str]:
    """What is wrong between the practice's schema and its fidelities."""
    return practice.schema.fidelity_errors(list(practice.fidelities.entries))


def _node_fidelities(practice) -> dict[str, list[str]]:
    """Each node type of the practice's schema with the fidelities it belongs to."""
    return practice.schema.node_fidelities(list(practice.fidelities.entries))


with description("a practice's schema"):
    with context("of every practice"):
        with it("should name only fidelities the practice has"):
            errors = {key: _fidelity_errors(PracticeCatalogue.create(key)) for key in PracticeCatalogue.keys()}
            expect(errors).to(equal({key: [] for key in PracticeCatalogue.keys()}))

    with context("of stories"):
        with it("should give map-level nodes to the story map and every higher fidelity"):
            mapping = _node_fidelities(PracticeCatalogue.create("stories"))
            expect(mapping["epic"][0]).to(equal("story_map"))

        with it("should give scenario nodes to scenarios first"):
            mapping = _node_fidelities(PracticeCatalogue.create("stories"))
            expect([mapping[node][0] for node in ("scenario", "step", "example")]).to(equal(["scenarios"] * 3))

    with context("of ddd"):
        with it("should give an entity the fidelity that creates it and every higher one"):
            expect(_node_fidelities(PracticeCatalogue.create("ddd"))["entity"]).to(equal(["model", "tactics"]))

        with it("should give the types the model draws, nested under the aggregate, to the model first"):
            mapping = _node_fidelities(PracticeCatalogue.create("ddd"))
            drawn = {mapping[name][0] for name in ("entityRoot", "entity", "valueObject", "repository")}
            expect(drawn).to(equal({"model"}))

        with it("should give the types tactics adds to tactics only"):
            mapping = _node_fidelities(PracticeCatalogue.create("ddd"))
            added = {tuple(mapping[name]) for name in ("domainEvent", "domainService", "factory", "specification")}
            expect(added).to(equal({("tactics",)}))
