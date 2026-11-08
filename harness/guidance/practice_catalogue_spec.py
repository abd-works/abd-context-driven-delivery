"""The practice catalogue: the one list of practices, and the toolset an action lists for a practice's or fidelity's slug."""
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import be, be_none, equal, expect, raise_error
from mamba import before, description, it

from harness.guidance.practice_catalogue import PracticeCatalogue, UnknownPractice
import cdd_guidance.practices  # noqa: F401 - registers the practices with the practice catalogue
import cdd_guidance.actions  # noqa: F401 - registers the actions with the action catalogue

_STORIES = "cdd_guidance.practices.stories.stories:Stories"


with description("the practice catalogue"):
    with it("should list the practices in the order the approach walks them"):
        expect(PracticeCatalogue.keys()).to(equal(("stories", "ddd", "ux", "clean_engineering", "bdd")))

    with it("should name a practice key it does not hold as an unknown practice"):
        expect(lambda: PracticeCatalogue.create("clean-engineering")).to(raise_error(UnknownPractice))

    with description("that is asked for the toolset a slug names"):
        with it("should name the practice's toolset for the practice's slug"):
            expect(PracticeCatalogue.toolset_ref("stories")).to(equal(_STORIES))

        with it("should name the practice's toolset and the fidelity for a fidelity's slug"):
            expect(PracticeCatalogue.toolset_ref("stories-story-map")).to(
                equal({"toolset": _STORIES, "fidelity": "story_map"})
            )

        with it("should name the fidelity for its bare name in kebab case"):
            expect(PracticeCatalogue.toolset_ref("story-map")).to(equal({"toolset": _STORIES, "fidelity": "story_map"}))

        with it("should name the fidelity for its bare name in snake case"):
            expect(PracticeCatalogue.toolset_ref("story_map")).to(equal({"toolset": _STORIES, "fidelity": "story_map"}))

        with it("should name nothing for a slug no practice goes by"):
            expect(PracticeCatalogue.toolset_ref("astrology")).to(be_none)

    with description("that makes a set of practices together"):
        with before.all:
            self.made = {practice.key: practice for practice in PracticeCatalogue.create_all()}
            stories = self.made["stories"]
            stories.work_at("acceptance_tests")
            self.companion = stories.fidelities.current.clean_engineering

        with it("should give a fidelity's companion from the Clean Engineering practice of the same set"):
            expect(self.companion.practice_guidance).to(be(self.made["clean_engineering"]))

        with it("should hold the practice an extending practice builds on from the same set"):
            expect(self.made["ddd"].extended).to(be(self.made["clean_engineering"]))
