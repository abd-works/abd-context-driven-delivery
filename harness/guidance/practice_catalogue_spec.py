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



with description("the practice catalogue"):
    with it("should list the practices in the order the approach walks them"):
        expect(PracticeCatalogue.keys()).to(equal(("stories", "ddd", "ux", "clean_engineering", "bdd")))

    with it("should name a practice key it does not hold as an unknown practice"):
        expect(lambda: PracticeCatalogue.create("clean-engineering")).to(raise_error(UnknownPractice))

    with description("whose practice is asked for the guidance a slug names"):
        with before.all:
            self.stories = PracticeCatalogue.create("stories")

        with it("should answer itself for the practice's slug"):
            expect(self.stories.answers_to("stories")).to(be(self.stories))

        with it("should answer its own fidelity for a fidelity's slug"):
            expect(self.stories.answers_to("stories-story-map")).to(be(self.stories.fidelities["story_map"]))

        with it("should answer its own fidelity for the fidelity's bare name in kebab case"):
            expect(self.stories.fidelity_called("story-map")).to(be(self.stories.fidelities["story_map"]))

        with it("should answer its own fidelity for the fidelity's bare name in snake case"):
            expect(self.stories.fidelity_called("story_map")).to(be(self.stories.fidelities["story_map"]))

        with it("should answer nothing for a slug it does not go by"):
            expect(self.stories.answers_to("astrology")).to(be_none)

    with description("whose practice is asked to work at a fidelity"):
        with before.all:
            self.stories = PracticeCatalogue.create("stories")
            self.ddd = PracticeCatalogue.create("ddd")

        with it("should hold that fidelity as its current one"):
            fidelity = self.stories.fidelities["scenarios"]
            expect(self.stories.work_at(fidelity)).to(be(self.stories.fidelities.current))

        with it("should refuse a fidelity of another practice"):
            expect(lambda: self.stories.work_at(self.ddd.fidelities["model"])).to(raise_error(ValueError))

    with description("that makes a set of practices together"):
        with before.all:
            self.made = {practice.key: practice for practice in PracticeCatalogue.create_all()}
            stories = self.made["stories"]
            stories.work_at(stories.fidelities["acceptance_tests"])
            self.companion = stories.fidelities.current.clean_engineering

        with it("should give a fidelity's companion from the Clean Engineering practice of the same set"):
            expect(self.companion.practice_guidance).to(be(self.made["clean_engineering"]))

        with it("should hold the practice an extending practice builds on from the same set"):
            expect(self.made["ddd"].extended).to(be(self.made["clean_engineering"]))
